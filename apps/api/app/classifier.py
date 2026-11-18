import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

import joblib
import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger("respiracidadao.classifier")

# Limiares derivados da base real UCI Air Quality (indices dos sensores MOx, mesma escala do ESP32).
# gas_voc sozinho separa as 3 classes com F1 macro de 0,83; e a regra que o ESP32 usa offline.
THRESHOLDS: Dict[str, Tuple[float, float]] = {
    "gas_voc": (830.0, 1140.0),
    "gas_co": (1010.0, 1280.0),
}

# Ordem das entradas dos modelos 06 (ML) e 08 (rede neural): o que o ESP32 mede.
MODEL_INPUTS = ["gas_co", "gas_voc", "temperatura_c", "umidade_pct"]

HF_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
HF_ENDPOINT = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

RISK_LABELS = ["normal", "atencao", "critico"]


def classify_threshold(metrica: str, valor: float) -> Tuple[Literal["normal", "atencao", "critico"], bool]:
    """Local deterministic risk classifier (always available, zero network dependency)."""
    low, high = THRESHOLDS[metrica]
    if valor >= high:
        return "critico", True
    if valor >= low:
        return "atencao", True
    return "normal", False


def analyze_report_sentiment(relato: str) -> Tuple[str, Optional[float], str]:
    """Calls Hugging Face Inference Router if HF_TOKEN is configured; falls back gracefully on failure."""
    if not relato.strip():
        return "sem_relato", None, "local-vazio"

    hf_token = os.getenv("HF_TOKEN", "").strip()
    if not hf_token:
        return _heuristic_pt_sentiment(relato)

    body = json.dumps({"inputs": relato[:400]}).encode("utf-8")
    req = urllib.request.Request(
        HF_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        # HF returns [[{label, score}, ...]] or [{label, score}, ...]
        candidates = raw[0] if raw and isinstance(raw[0], list) else raw
        if isinstance(candidates, list) and candidates:
            top = max(candidates, key=lambda x: float(x.get("score", 0.0)))
            return str(top.get("label", "neutral")), round(float(top.get("score", 0.0)), 4), "huggingface-router"
    except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        logger.warning("HF sentiment fallback triggered (%s): ingestion continues normally.", exc)
    return _heuristic_pt_sentiment(relato)


def _heuristic_pt_sentiment(relato: str) -> Tuple[str, Optional[float], str]:
    text = relato.lower()
    urgent_terms = ["fumaça", "fumaca", "queimada", "fogo", "ardencia", "ardência", "tosse", "falta de ar", "sufocando", "critico", "crítico", "emergencia", "emergência", "hospital"]
    caution_terms = ["cheiro", "neblina", "cinza", "seco", "poeira", "desconforto", "irritacao", "irritação"]
    if any(t in text for t in urgent_terms):
        return "negative", 0.91, "fallback-local-lexicon"
    if any(t in text for t in caution_terms):
        return "neutral", 0.72, "fallback-local-lexicon"
    return "positive", 0.80, "fallback-local-lexicon"


class AirQualityMLP(nn.Module):
    """Deep regularized MLP matching 08-neural-networks notebook."""

    def __init__(self, in_features: int, hidden_dims: List[int], num_classes: int = 3, dropout: float = 0.25):
        super().__init__()
        layers: List[nn.Module] = []
        prev = in_features
        for h in hidden_dims:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.BatchNorm1d(h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev = h
        layers.append(nn.Linear(prev, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ModelBundle:
    """Loads exported ML (06) and PyTorch NN (08) artifacts for live /predict inference."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.ml_path = root_dir / "packages" / "ml-modelling" / "artifacts" / "best_ml_model.joblib"
        self.nn_weights_path = root_dir / "packages" / "neural-networks" / "artifacts" / "air_quality_mlp.pt"
        self.nn_meta_path = root_dir / "packages" / "neural-networks" / "artifacts" / "nn_metadata.joblib"
        self.ml_model = None
        self.nn_model: Optional[AirQualityMLP] = None
        self.nn_scaler = None
        self.nn_features: List[str] = []
        self.reload()

    def reload(self) -> None:
        if self.ml_path.exists():
            try:
                self.ml_model = joblib.load(self.ml_path)
            except Exception as exc:
                logger.warning("Failed loading ML artifact: %s", exc)
        if self.nn_weights_path.exists() and self.nn_meta_path.exists():
            try:
                meta = joblib.load(self.nn_meta_path)
                self.nn_scaler = meta["scaler"]
                self.nn_features = meta["features"]
                hidden = meta["hidden_dims"]
                dropout = meta.get("dropout", 0.25)
                model = AirQualityMLP(len(self.nn_features), hidden, num_classes=3, dropout=dropout)
                model.load_state_dict(torch.load(self.nn_weights_path, map_location="cpu", weights_only=True))
                model.eval()
                self.nn_model = model
            except Exception as exc:
                logger.warning("Failed loading NN artifact: %s", exc)

    def predict(self, payload: dict) -> dict:
        row = np.array([[float(payload[k]) for k in MODEL_INPUTS]], dtype=np.float32)
        result: Dict[str, object] = {}

        if self.ml_model is not None:
            probs = self.ml_model.predict_proba(row)[0]
            step = self.ml_model.named_steps.get("model") if hasattr(self.ml_model, "named_steps") else self.ml_model
            result["ml"] = _verdict(type(step).__name__, probs)

        if self.nn_model is not None and self.nn_scaler is not None:
            with torch.no_grad():
                logits = self.nn_model(torch.tensor(self.nn_scaler.transform(row), dtype=torch.float32))
                probs = torch.softmax(logits, dim=1).numpy()[0]
            result["nn"] = _verdict("AirQualityMLP (PyTorch)", probs)

        risco, _ = classify_threshold("gas_voc", payload["gas_voc"])
        result["regra_local"] = {"classe": risco}
        return result

    def field_risk(self, readings: dict) -> Tuple[Optional[str], Optional[float]]:
        """Veredito do Random Forest para uma leitura completa do ESP32; (None, None) se faltar dado."""
        if self.ml_model is None or any(readings.get(k) is None for k in MODEL_INPUTS):
            return None, None
        row = np.array([[float(readings[k]) for k in MODEL_INPUTS]], dtype=np.float32)
        probs = self.ml_model.predict_proba(row)[0]
        idx = int(np.argmax(probs))
        return RISK_LABELS[idx], round(float(probs[idx]), 4)


def _verdict(modelo: str, probs) -> dict:
    idx = int(np.argmax(probs))
    return {
        "modelo": modelo,
        "classe": RISK_LABELS[idx],
        "probabilidades": {RISK_LABELS[i]: round(float(probs[i]), 4) for i in range(3)},
    }
