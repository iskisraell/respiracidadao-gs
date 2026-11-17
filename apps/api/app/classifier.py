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

THRESHOLDS: Dict[str, Tuple[float, float]] = {
    "fumaca_ppm": (120.0, 250.0),      # MQ-2 / MQ-135 smoke/gas ppm
    "co_mg_m3": (4.0, 9.0),            # Carbon Monoxide (WHO / CONAMA inspired)
    "no2_ug_m3": (100.0, 200.0),       # Nitrogen Dioxide
    "pm25_ug_m3": (25.0, 50.0),        # Particulate matter 2.5
    "c6h6_ug_m3": (5.0, 15.0),         # Benzene
}

HF_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
HF_ENDPOINT = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

RISK_LABELS = ["normal", "atencao", "critico"]


def classify_threshold(metrica: str, valor: float) -> Tuple[Literal["normal", "atencao", "critico"], bool]:
    """Local deterministic risk classifier (always available, zero network dependency)."""
    low, high = THRESHOLDS.get(metrica.lower(), (120.0, 250.0))
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
        row = np.array([[
            payload["co_sensor_s1"],
            payload["c6h6_gt"],
            payload["nmhc_sensor_s2"],
            payload["nox_gt"],
            payload["nox_sensor_s3"],
            payload["no2_gt"],
            payload["no2_sensor_s4"],
            payload["o3_sensor_s5"],
            payload["temperatura_c"],
            payload["umidade_pct"],
            payload["umidade_absoluta"],
        ]], dtype=np.float32)

        result: Dict[str, object] = {
            "ml_disponivel": self.ml_model is not None,
            "nn_disponivel": self.nn_model is not None,
        }

        if self.ml_model is not None:
            ml_probs = self.ml_model.predict_proba(row)[0]
            ml_idx = int(np.argmax(ml_probs))
            result["ml"] = {
                "modelo": type(self.ml_model.named_steps["model"]).__name__ if hasattr(self.ml_model, "named_steps") else type(self.ml_model).__name__,
                "classe": RISK_LABELS[ml_idx],
                "probabilidades": {RISK_LABELS[i]: round(float(ml_probs[i]), 4) for i in range(3)},
            }

        if self.nn_model is not None and self.nn_scaler is not None:
            scaled = self.nn_scaler.transform(row)
            with torch.no_grad():
                logits = self.nn_model(torch.tensor(scaled, dtype=torch.float32))
                probs = torch.softmax(logits, dim=1).numpy()[0]
            nn_idx = int(np.argmax(probs))
            result["nn"] = {
                "modelo": "AirQualityMLP (PyTorch)",
                "classe": RISK_LABELS[nn_idx],
                "probabilidades": {RISK_LABELS[i]: round(float(probs[i]), 4) for i in range(3)},
            }

        # Fallback rule if models haven't been trained yet
        if "ml" not in result and "nn" not in result:
            risco, _ = classify_threshold("no2_ug_m3", payload["no2_gt"])
            result["fallback_limiar"] = {"classe": risco}

        return result
