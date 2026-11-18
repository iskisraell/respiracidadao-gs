import json
import logging
import os
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .classifier import (
    HF_MODEL,
    THRESHOLDS,
    ModelBundle,
    analyze_report_sentiment,
    classify_threshold,
)
from .schemas import OcorrenciaIn, OcorrenciaOut, PredictIn, SimulateRequest
from .security import (
    SecurityAuditor,
    SlidingWindowRateLimiter,
    compute_record_hash,
    contains_markup,
    get_client_ip,
    sanitize_text,
    verify_api_key,
)
from .storage import OccurrenceStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("respiracidadao.api")

ROOT_DIR = Path(__file__).resolve().parents[3]
RUNTIME_DIR = Path(os.getenv("RESPIRA_DATA_DIR", str(ROOT_DIR / "data" / "runtime")))

store = OccurrenceStore(RUNTIME_DIR)
auditor = SecurityAuditor(RUNTIME_DIR / "security_audit.jsonl")
rate_limiter = SlidingWindowRateLimiter()
models = ModelBundle(ROOT_DIR)

app = FastAPI(
    title="RespiraCidadão API",
    version="1.0.0",
    description="API integradora CitizenTech para monitoramento de fumaça, qualidade do ar e risco respiratório.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    client_ip = get_client_ip(request)
    errors = [
        {"campo": ".".join(str(p) for p in err.get("loc", [])), "mensagem": err.get("msg", "")}
        for err in exc.errors()
    ]
    logger.warning("LEITURA DESCARTADA - validacao falhou (%s): %s", client_ip, errors)
    auditor.record(
        event="validation_rejected",
        severity="warning",
        client_ip=client_ip,
        detail=f"Payload inválido rejeitado em {request.url.path}: {errors}",
        status_code=400,
    )
    return JSONResponse(
        status_code=400,
        content={"erro": "Campos obrigatórios ausentes ou inválidos.", "detalhes": errors},
    )


def _ingest_occurrence(payload: OcorrenciaIn, client_ip: str, source_tag: str = "api") -> dict:
    """Valida, classifica (regra local + Random Forest + sentimento do relato) e grava em SQLite e CSV."""
    clean_relato = sanitize_text(payload.relato)
    nivel_risco, alerta = classify_threshold(payload.metrica, payload.valor)
    ia_sentimento, ia_confianca, ia_fonte = analyze_report_sentiment(clean_relato)

    gas_voc = payload.valor if payload.metrica == "gas_voc" else None
    gas_co = payload.gas_co if payload.gas_co is not None else (payload.valor if payload.metrica == "gas_co" else None)
    ia_risco, ia_risco_prob = models.field_risk(
        {"gas_co": gas_co, "gas_voc": gas_voc, "temperatura_c": payload.temperatura_c, "umidade_pct": payload.umidade_pct}
    )

    logger.info(
        "LEITURA %s: %s %s=%.1f gas_co=%s T=%s UR=%s -> regra=%s modelo=%s (%s)",
        source_tag, payload.dispositivo_id, payload.metrica, payload.valor, gas_co,
        payload.temperatura_c, payload.umidade_pct, nivel_risco, ia_risco, ia_risco_prob,
    )
    if nivel_risco == "critico":
        logger.warning("ALERTA CRITICO: %s %s=%.1f", payload.dispositivo_id, payload.metrica, payload.valor)

    record = store.insert(
        {
            "dispositivo_id": payload.dispositivo_id,
            "tipo": payload.tipo,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "metrica": payload.metrica,
            "valor": float(payload.valor),
            "gas_co": gas_co,
            "temperatura_c": payload.temperatura_c,
            "umidade_pct": payload.umidade_pct,
            "relato": clean_relato,
            "ia_sentimento": ia_sentimento,
            "ia_confianca": ia_confianca,
            "ia_fonte": ia_fonte,
            "nivel_risco": nivel_risco,
            "alerta": alerta,
            "ia_risco": ia_risco,
            "ia_risco_prob": ia_risco_prob,
        }
    )

    if contains_markup(payload.relato):
        auditor.record(
            event="xss_sanitized",
            severity="warning",
            client_ip=client_ip,
            detail=f"Relato do registro #{record['id']} tinha marcação HTML e foi sanitizado.",
            status_code=201,
        )
    auditor.record(
        event="occurrence_ingested",
        severity="warning" if nivel_risco == "critico" else "info",
        client_ip=client_ip,
        detail=f"Leitura #{record['id']} ({payload.dispositivo_id}): regra {nivel_risco}, modelo {ia_risco or 'sem dados'}.",
        status_code=201,
    )
    return record


@app.get("/health")
def health():
    return {
        "status": "ok",
        "servico": "RespiraCidadão API",
        "modelo_sentimento": HF_MODEL,
        "ia_hf_configurada": bool(os.getenv("HF_TOKEN", "").strip()),
        "ml_carregado": models.ml_model is not None,
        "nn_carregado": models.nn_model is not None,
        "limiares": THRESHOLDS,
    }


@app.post("/ocorrencias", response_model=OcorrenciaOut, status_code=201)
def create_ocorrencia(payload: OcorrenciaIn, request: Request):
    client_ip = get_client_ip(request)
    allowed, remaining, retry_after = rate_limiter.check(client_ip)
    if not allowed:
        logger.warning("RATE LIMIT ATINGIDO para ip=%s retry_after=%ss", client_ip, retry_after)
        auditor.record(
            event="rate_limit_blocked",
            severity="critical",
            client_ip=client_ip,
            detail=f"Excesso de requisições bloqueado ({rate_limiter.max_requests}/{rate_limiter.window_sec}s).",
            status_code=429,
        )
        raise HTTPException(
            status_code=429,
            detail=f"Limite de requisições excedido. Tente novamente em {retry_after}s.",
            headers={"Retry-After": str(retry_after), "X-RateLimit-Remaining": "0"},
        )

    record = _ingest_occurrence(payload, client_ip=client_ip, source_tag="http-post")
    return JSONResponse(
        status_code=201,
        content=record,
        headers={"X-RateLimit-Remaining": str(remaining)},
    )


@app.get("/ocorrencias", response_model=List[OcorrenciaOut])
def list_ocorrencias(
    risco: Optional[str] = Query(default=None),
    dispositivo_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
):
    return store.list_all(risco=risco, dispositivo_id=dispositivo_id, limit=limit)


@app.get("/indicadores")
def get_indicadores():
    return store.compute_indicators()


@app.post("/predict")
def predict_risk(payload: PredictIn, request: Request):
    client_ip = get_client_ip(request)
    if models.ml_model is None or models.nn_model is None:
        models.reload()  # pick up artifacts trained after startup without reloading on every call
    result = models.predict(payload.model_dump())
    auditor.record(
        event="ai_prediction",
        severity="info",
        client_ip=client_ip,
        detail=f"Inferência executada (ML={result.get('ml_disponivel')}, NN={result.get('nn_disponivel')}).",
        status_code=200,
    )
    return result


@app.post("/simulate")
def simulate_scenarios(body: SimulateRequest, request: Request):
    client_ip = get_client_ip(request)
    # Medianas de cada classe na base UCI: o que o ESP32 leria numa hora típica de cada nível.
    base = {"tipo": body.tipo, "metrica": "gas_voc"}
    scenarios = {
        "normal": OcorrenciaIn(
            **base, dispositivo_id="esp32-ubs-vila-maria", latitude=-23.5122, longitude=-46.5917,
            valor=706.0, gas_co=925.0, temperatura_c=18.0, umidade_pct=55.0,
            relato="Manhã limpa, sem cheiro de fumaça.",
        ),
        "atencao": OcorrenciaIn(
            **base, dispositivo_id="esp32-centro-01", latitude=-23.5505, longitude=-46.6333,
            valor=980.0, gas_co=1120.0, temperatura_c=24.0, umidade_pct=42.0,
            relato="Trânsito parado na frente da escola, cheiro de escapamento.",
        ),
        "critico": OcorrenciaIn(
            **base, dispositivo_id="esp32-escola-zona-norte", latitude=-23.4892, longitude=-46.6208,
            valor=1280.0, gas_co=1383.0, temperatura_c=31.0, umidade_pct=34.0,
            relato="Fumaça de queimada, crianças tossindo no pátio.",
        ),
    }

    keys = ["normal", "atencao", "critico"] if body.cenario == "todos" else [body.cenario]
    resultados = []
    for k in keys:
        item = scenarios[k]
        rec = _ingest_occurrence(item, client_ip=client_ip, source_tag=f"sim-{k}")
        resultados.append({"cenario": k, "enviado": item.model_dump(), "registro": rec})

    return {"executados": len(resultados), "resultados": resultados}


@app.get("/stats/summary")
def get_stats_summary():
    stats_path = ROOT_DIR / "packages" / "stats-r-python" / "artifacts" / "stats_summary.json"
    ml_path = ROOT_DIR / "packages" / "ml-modelling" / "artifacts" / "ml_metrics.json"
    nn_path = ROOT_DIR / "packages" / "neural-networks" / "artifacts" / "nn_metrics.json"

    def _read_json(p: Path):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return None

    return {
        "estatistica": _read_json(stats_path),
        "machine_learning": _read_json(ml_path),
        "redes_neurais": _read_json(nn_path),
    }


@app.get("/security/audit")
def get_security_audit(limit: int = Query(default=40, ge=1, le=100)):
    return {
        "rate_limit": {
            "max_requests": rate_limiter.max_requests,
            "window_sec": rate_limiter.window_sec,
        },
        "controls": [
            "Rate Limiting (Sliding Window HTTP 429)",
            "Autenticação administrativa via X-API-Key (HMAC)",
            "Sanitização de texto contra XSS e log injection",
            "Hash SHA-256 de integridade por ocorrência",
            "Trilha de auditoria JSONL persistida",
        ],
        "events": auditor.list_events(limit=limit),
    }


@app.get("/security/verify/{record_id}")
def verify_record_integrity(record_id: int, request: Request):
    rec = store.get_by_id(record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada.")
    recomputed = compute_record_hash(rec)
    integro = recomputed == rec["hash_integridade"]
    auditor.record(
        event="integrity_check",
        severity="info" if integro else "critical",
        client_ip=get_client_ip(request),
        detail=f"Verificação SHA-256 do registro #{record_id}: {'ÍNTEGRO' if integro else 'ADULTERADO'}.",
        status_code=200,
    )
    return {
        "id": record_id,
        "integro": integro,
        "hash_armazenado": rec["hash_integridade"],
        "hash_recalculado": recomputed,
    }


@app.delete("/ocorrencias", dependencies=[Depends(verify_api_key)])
def clear_ocorrencias(request: Request):
    store.clear_all()
    auditor.record(
        event="admin_clear",
        severity="warning",
        client_ip=get_client_ip(request),
        detail="Histórico limpo por chamada autenticada via X-API-Key.",
        status_code=200,
    )
    return {"status": "limpo"}
