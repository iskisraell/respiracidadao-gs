"""
Central do RespiraCidadão na nuvem: recebe a leitura do sensor por uma Function URL,
classifica o nível, lê o relato com IA (quando houver) e grava no PostgreSQL (RDS).
Os logs ficam no CloudWatch. Mesmo contrato e mesmos limites do firmware e da API.
"""

import base64
import json
import re
import logging
import math
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pg8000 as driver

logger = logging.getLogger()
logger.setLevel(logging.INFO)

HF_MODEL = os.environ.get("HF_MODEL", "cardiffnlp/twitter-xlm-roberta-base-sentiment")
HF_API_URL = os.environ.get("HF_API_URL", "https://router.huggingface.co/hf-inference/models")
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()

# Índices dos sensores de gás, na escala da base real de 6.941 horas.
LIMIARES = {
    "gas_voc": {"atencao": 830.0, "critico": 1140.0},
    "gas_co": {"atencao": 1010.0, "critico": 1280.0},
}
TIPOS_VALIDOS = {"esp32", "app"}
LEITURAS_EXTRAS = ("gas_co", "temperatura_c", "umidade_pct")
COLUNAS = (
    "dispositivo_id", "tipo_dispositivo", "latitude", "longitude", "metrica", "valor",
    *LEITURAS_EXTRAS, "relato", "sentimento", "confianca", "nivel_risco", "medido_em",
)
# Mesmas faixas válidas da API (apps/api/app/schemas.py).
FAIXAS = {
    "valor": (0.0, 100000.0),
    "gas_co": (0.0, 5000.0),
    "temperatura_c": (-40.0, 85.0),
    "umidade_pct": (0.0, 100.0),
    "latitude": (-90.0, 90.0),
    "longitude": (-180.0, 180.0),
}
DISPOSITIVO_RE = re.compile(r"^[A-Za-z0-9_.:\-]{2,64}$")
LIMITE_LOG_PAYLOAD = 2000
LIMITE_RELATO = 500


def conectar():
    return driver.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        # O RDS com PostgreSQL 15+ recusa conexão sem SSL (rds.force_ssl=1).
        ssl_context=os.environ.get("DB_SSL", "1") != "0" or None,
    )


def gravar_ocorrencia(dados):
    sql = (
        f"INSERT INTO ocorrencias ({', '.join(COLUNAS)}) "
        f"VALUES ({', '.join(['%s'] * len(COLUNAS))}) RETURNING id, criado_em"
    )
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(dados[c] for c in COLUNAS))
        novo_id, criado_em = cur.fetchone()
        conn.commit()
        return novo_id, criado_em
    finally:
        conn.close()


def listar_ocorrencias(limite=20):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, dispositivo_id, tipo_dispositivo, metrica, valor, gas_co,
                   nivel_risco, sentimento, confianca, relato, medido_em, criado_em
              FROM ocorrencias
             ORDER BY id DESC
             LIMIT %s
            """,
            (limite,),
        )
        colunas = [
            "id",
            "dispositivo_id",
            "tipo_dispositivo",
            "metrica",
            "valor",
            "gas_co",
            "nivel_risco",
            "sentimento",
            "confianca",
            "relato",
            "medido_em",
            "criado_em",
        ]
        return [dict(zip(colunas, linha)) for linha in cur.fetchall()]
    finally:
        conn.close()


def classificar_risco(metrica, valor):
    faixa = LIMIARES.get(metrica)
    if faixa is None or valor is None:
        return "desconhecido"
    if valor >= faixa["critico"]:
        return "critico"
    if valor >= faixa["atencao"]:
        return "atencao"
    return "normal"


def analisar_relato(texto):
    if not texto or not HF_TOKEN:
        return None, None

    url = f"{HF_API_URL.rstrip('/')}/{HF_MODEL}"
    corpo = json.dumps({"inputs": texto}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=corpo,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            saida = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        logger.warning("Hugging Face respondeu %s: %s", erro.code, erro.read()[:200])
        return None, None
    except Exception as erro:
        logger.warning("Falha ao chamar Hugging Face (%s): ingestao segue normalmente.", erro)
        return None, None

    # A resposta da IA nunca pode derrubar a ingestao (ex.: {"error": ...} com HTTP 200).
    try:
        lista = saida[0] if saida and isinstance(saida[0], list) else saida
        melhor = max(lista, key=lambda item: float(item.get("score", 0.0)))
        return str(melhor.get("label")), round(float(melhor.get("score", 0.0)), 4)
    except (KeyError, IndexError, TypeError, ValueError, AttributeError) as erro:
        logger.warning("Resposta inesperada do Hugging Face (%s): ingestao segue normalmente.", erro)
        return None, None


def _numero(valor, nome, obrigatorio=False):
    """Converte para float finito; devolve (valor, erro)."""
    if valor is None:
        return None, (f"{nome} ausente" if obrigatorio else None)
    if isinstance(valor, bool):
        return None, f"{nome} deve ser numerico"
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None, f"{nome} deve ser numerico"
    if not math.isfinite(numero):
        return None, f"{nome} deve ser um numero finito"
    return numero, None


def _data_medicao(texto):
    """Mesma regra da API local: ISO 8601, no maximo 5 minutos no futuro; devolve (data, erro)."""
    agora = datetime.now(timezone.utc)
    if not texto:
        return agora, None
    try:
        data = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None, "medido_em deve estar no formato ISO 8601"
    data = (data if data.tzinfo else data.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    if data > agora + timedelta(minutes=5):
        return None, "medido_em nao pode estar no futuro"
    return data, None


def _corpo_requisicao(evento):
    bruto = evento.get("body") or "{}"
    if evento.get("isBase64Encoded"):
        bruto = base64.b64decode(bruto).decode("utf-8", "replace")
    return bruto


def _limpar_texto(texto):
    """Mesma limpeza da API: tira tags, sinais < > e caracteres de controle."""
    sem_tags = re.sub(r"[<>]", "", re.sub(r"<[^>]*>", " ", str(texto)))
    return " ".join(re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", sem_tags).split())


def rota_ingestao(evento):
    bruto = _corpo_requisicao(evento)
    logger.info("PAYLOAD RECEBIDO: %s", bruto[:LIMITE_LOG_PAYLOAD])

    try:
        payload = json.loads(bruto)
    except json.JSONDecodeError:
        logger.warning("LEITURA DESCARTADA - JSON invalido")
        return resposta(400, {"erro": "corpo nao e um JSON valido"})
    if not isinstance(payload, dict):
        logger.warning("LEITURA DESCARTADA - corpo deve ser um objeto JSON")
        return resposta(400, {"erro": "corpo deve ser um objeto JSON"})

    obrigatorios = ["dispositivo_id", "valor"]
    faltando = [c for c in obrigatorios if payload.get(c) is None or str(payload.get(c)).strip() == ""]
    if faltando:
        logger.warning("LEITURA DESCARTADA - campos ausentes: %s", faltando)
        return resposta(400, {"erro": "campos obrigatorios ausentes", "campos": faltando})

    valor, erro_valor = _numero(payload["valor"], "valor", obrigatorio=True)
    latitude, erro_lat = _numero(payload.get("latitude"), "latitude")
    longitude, erro_lon = _numero(payload.get("longitude"), "longitude")
    extras = {c: _numero(payload.get(c), c) for c in LEITURAS_EXTRAS}
    tipo_disp = str(payload.get("tipo_dispositivo") or payload.get("tipo") or "esp32").strip().lower()
    erros = [e for e in (erro_valor, erro_lat, erro_lon, *(err for _, err in extras.values())) if e]
    if tipo_disp not in TIPOS_VALIDOS:
        erros.append(f"tipo_dispositivo deve ser um de {sorted(TIPOS_VALIDOS)}")
    metrica = str(payload.get("metrica") or "gas_voc").strip()  # mesmo padrão da API local
    if metrica not in LIMIARES:
        erros.append(f"metrica deve ser um de {sorted(LIMIARES)}")
    if not DISPOSITIVO_RE.match(str(payload["dispositivo_id"]).strip()):
        erros.append("dispositivo_id aceita só letras, números e . _ : - (2 a 64)")
    numeros = {"valor": valor, "latitude": latitude, "longitude": longitude, **{c: v for c, (v, _) in extras.items()}}
    for campo, (minimo, maximo) in FAIXAS.items():
        v = numeros.get(campo)
        if v is not None and not (minimo <= v <= maximo):
            erros.append(f"{campo} fora da faixa {minimo} a {maximo}")
    relato_bruto = payload.get("relato")
    if relato_bruto is not None and len(str(relato_bruto)) > LIMITE_RELATO:
        erros.append(f"relato passa de {LIMITE_RELATO} caracteres")
    if erros:
        logger.warning("LEITURA DESCARTADA - campos invalidos: %s", erros)
        return resposta(400, {"erro": "campos invalidos", "detalhes": erros})
    medido_em, erro_data = _data_medicao(payload.get("medido_em"))
    if erro_data:
        return resposta(400, {"erro": "campos invalidos", "detalhes": [erro_data]})

    relato = payload.get("relato")
    relato = _limpar_texto(relato) if relato is not None else None
    dados = {
        "dispositivo_id": str(payload["dispositivo_id"]).strip(),
        "tipo_dispositivo": tipo_disp,
        "latitude": latitude,
        "longitude": longitude,
        "metrica": metrica,
        "valor": valor,
        **{c: v for c, (v, _) in extras.items()},
        "relato": relato,
        "medido_em": medido_em,
    }

    logger.info(
        "DISPOSITIVO=%s TIPO=%s GPS=(%s, %s) %s=%s",
        dados["dispositivo_id"],
        dados["tipo_dispositivo"],
        dados["latitude"],
        dados["longitude"],
        dados["metrica"],
        dados["valor"],
    )

    dados["nivel_risco"] = classificar_risco(dados["metrica"], dados["valor"])
    dados["sentimento"], dados["confianca"] = analisar_relato(dados["relato"])

    logger.info(
        "CLASSIFICACAO risco=%s sentimento=%s confianca=%s",
        dados["nivel_risco"],
        dados["sentimento"],
        dados["confianca"],
    )
    if dados["nivel_risco"] == "critico":
        logger.warning(
            "ALERTA CIDADAO: %s em %s atingiu %s (%s)",
            dados["metrica"],
            dados["dispositivo_id"],
            dados["valor"],
            dados["nivel_risco"],
        )

    novo_id, criado_em = gravar_ocorrencia(dados)
    logger.info("GRAVADO NO RDS id=%s em %s", novo_id, criado_em)

    return resposta(
        201,
        {
            "id": novo_id,
            "dispositivo_id": dados["dispositivo_id"],
            "tipo_dispositivo": dados["tipo_dispositivo"],
            "latitude": dados["latitude"],
            "longitude": dados["longitude"],
            "metrica": dados["metrica"],
            "valor": dados["valor"],
            **{c: dados[c] for c in LEITURAS_EXTRAS},
            "nivel_risco": dados["nivel_risco"],
            "sentimento": dados["sentimento"],
            "confianca": dados["confianca"],
            "alerta": dados["nivel_risco"] == "critico",
            "medido_em": dados["medido_em"].isoformat(),
            "criado_em": criado_em,
        },
    )


def _serializar(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # NUMERIC(5,4) do RDS -> numero JSON, nao string
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def resposta(status, corpo):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(corpo, default=_serializar, ensure_ascii=False),
    }


def lambda_handler(evento, contexto):
    metodo = (evento.get("requestContext", {}).get("http", {}).get("method", "GET")).upper()
    caminho = evento.get("rawPath", "/")
    logger.info("REQUISICAO %s %s", metodo, caminho)

    try:
        if caminho == "/health":
            return resposta(200, {"status": "ok", "modelo": HF_MODEL, "ia_ativa": bool(HF_TOKEN)})
        if caminho == "/ocorrencias" and metodo == "POST":
            return rota_ingestao(evento)
        if caminho == "/ocorrencias" and metodo == "GET":
            return resposta(200, {"ocorrencias": listar_ocorrencias()})
        return resposta(404, {"erro": "rota nao encontrada", "caminho": caminho})
    except Exception:
        logger.exception("ERRO NAO TRATADO")
        return resposta(500, {"erro": "erro interno ao processar a requisicao"})  # detalhes ficam so no CloudWatch
