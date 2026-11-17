import hashlib
import hmac
import html
import json
import os
import re
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
TRUST_PROXY = os.getenv("RESPIRA_TRUST_PROXY", "").strip().lower() in {"1", "true", "yes"}

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_MARKUP_CHARS = re.compile(r"[<>]")


def sanitize_text(value: Optional[str]) -> str:
    """Escape HTML/script payloads and normalize whitespace to mitigate XSS/log injection."""
    if not value:
        return ""
    stripped = " ".join(_CONTROL_CHARS.sub(" ", value).split())
    return html.escape(stripped, quote=True)


def contains_markup(value: Optional[str]) -> bool:
    """True when the raw text carries HTML-like markup that sanitize_text neutralises."""
    return bool(value and _MARKUP_CHARS.search(value))


def compute_record_hash(payload: dict) -> str:
    """Compute deterministic SHA-256 integrity digest for a persisted occurrence."""
    canonical = {
        "dispositivo_id": payload.get("dispositivo_id"),
        "tipo": payload.get("tipo"),
        "metrica": payload.get("metrica"),
        "valor": round(float(payload.get("valor", 0.0)), 4),
        "nivel_risco": payload.get("nivel_risco"),
        "relato": payload.get("relato", ""),
        "criado_em": payload.get("criado_em"),
    }
    encoded = json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")
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
