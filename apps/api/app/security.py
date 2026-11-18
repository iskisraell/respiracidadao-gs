import hashlib
import hmac
import json
import os
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Header, HTTPException, Request

# Administrative API key comes ONLY from the environment (RESPIRA_API_KEY). No hardcoded fallback:
# when it is unset, protected routes fail closed instead of accepting a well-known default.
ADMIN_API_KEY = os.getenv("RESPIRA_API_KEY", "").strip()
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "30"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
# Only honour X-Forwarded-For when the API sits behind a trusted reverse proxy.
# Otherwise any client could spoof the header and bypass the per-IP rate limiter.
# Chave do selo de integridade. Com ela o selo é HMAC-SHA256: quem altera o banco sem a chave
# não consegue refazer o selo. Sem ela, cai para SHA-256 puro (detecta alteração acidental).
def _load_seal_key() -> bytes:
    """RESPIRA_SEAL_KEY do ambiente; sem ela, gera uma chave local fora do banco (arquivo 0600, ignorado pelo git)."""
    env = os.getenv("RESPIRA_SEAL_KEY", "").strip()
    if env:
        return env.encode("utf-8")
    data_dir = Path(os.getenv("RESPIRA_DATA_DIR", Path(__file__).resolve().parents[3] / "data" / "runtime"))
    key_file = Path(os.getenv("RESPIRA_SEAL_KEY_FILE", data_dir / "seal.key"))
    try:
        if key_file.exists():
            return key_file.read_text(encoding="utf-8").strip().encode("utf-8")
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key = secrets.token_hex(32)
        fd = os.open(str(key_file), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(key)
        return key.encode("utf-8")
    except OSError:
        return b""


SEAL_KEY = _load_seal_key()
TRUST_PROXY = os.getenv("RESPIRA_TRUST_PROXY", "").strip().lower() in {"1", "true", "yes"}

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_MARKUP_CHARS = re.compile(r"[<>]")
_TAGS = re.compile(r"<[^>]*>")


def sanitize_text(value: Optional[str]) -> str:
    """Remove tags e sinais < >, caracteres de controle e espaços repetidos.

    Não converte para entidades HTML: o app (React) já escapa o texto na tela, e entidades
    apareceriam cruas para quem lê (d&#x27;água). Fórmulas de planilha são tratadas no CSV.
    """
    if not value:
        return ""
    no_tags = _MARKUP_CHARS.sub("", _TAGS.sub(" ", value))
    return " ".join(_CONTROL_CHARS.sub(" ", no_tags).split())


def contains_markup(value: Optional[str]) -> bool:
    """True when the raw text carries HTML-like markup that sanitize_text neutralises."""
    return bool(value and _MARKUP_CHARS.search(value))


def compute_record_hash(payload: dict) -> str:
    """Selo de integridade de uma leitura: HMAC-SHA256 com RESPIRA_SEAL_KEY, ou SHA-256 sem a chave."""
    def num(key: str):
        v = payload.get(key)
        return None if v is None or v == "" else round(float(v), 4)

    canonical = {
        "dispositivo_id": payload.get("dispositivo_id"),
        "tipo": payload.get("tipo"),
        "latitude": num("latitude"),
        "longitude": num("longitude"),
        "metrica": payload.get("metrica"),
        "valor": num("valor"),
        "gas_co": num("gas_co"),
        "temperatura_c": num("temperatura_c"),
        "umidade_pct": num("umidade_pct"),
        "nivel_risco": payload.get("nivel_risco"),
        "ia_risco": payload.get("ia_risco"),
        "ia_risco_prob": num("ia_risco_prob"),
        "relato": payload.get("relato", ""),
        "alerta": bool(payload.get("alerta")),
        "ia_sentimento": payload.get("ia_sentimento"),
        "ia_confianca": num("ia_confianca"),
        "ia_fonte": payload.get("ia_fonte"),
        "criado_em": payload.get("criado_em"),
    }
    encoded = json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")
    if SEAL_KEY:
        return hmac.new(SEAL_KEY, encoded, hashlib.sha256).hexdigest()
    return hashlib.sha256(encoded).hexdigest()


class SlidingWindowRateLimiter:
    """Per-client sliding-window rate limiter (03 Cognitive Cybersecurity control)."""

    def __init__(self, max_requests: int = RATE_LIMIT_MAX_REQUESTS, window_sec: int = RATE_LIMIT_WINDOW_SEC):
        self.max_requests = max_requests
        self.window_sec = window_sec
        self._hits: Dict[str, deque] = defaultdict(deque)

    def reset(self) -> None:
        self._hits.clear()

    def check(self, client_key: str) -> tuple[bool, int, int]:
        now = time.monotonic()
        q = self._hits[client_key]
        cutoff = now - self.window_sec
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= self.max_requests:
            retry_after = max(1, int(self.window_sec - (now - q[0])))
            return False, 0, retry_after
        q.append(now)
        remaining = max(0, self.max_requests - len(q))
        return True, remaining, 0


class SecurityAuditor:
    """Writes structured security audit events to disk and exposes recent history."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._recent: deque = deque(maxlen=100)
        if self.log_path.exists():
            try:
                lines = self.log_path.read_text(encoding="utf-8").splitlines()[-100:]
                for line in lines:
                    if line.strip():
                        self._recent.append(json.loads(line))
            except Exception:
                pass

    def record(self, event: str, severity: str, client_ip: str, detail: str, status_code: int) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "severity": severity,
            "client_ip": client_ip,
            "status_code": status_code,
            "detail": detail,
        }
        self._recent.append(entry)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def list_events(self, limit: int = 40) -> List[dict]:
        return list(self._recent)[-limit:][::-1]


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> str:
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Autenticação administrativa não configurada (defina RESPIRA_API_KEY).")
    if not x_api_key or not hmac.compare_digest(x_api_key.encode("utf-8"), ADMIN_API_KEY.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Chave de API ausente ou inválida (X-API-Key).")
    return x_api_key


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for") if TRUST_PROXY else None
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"
