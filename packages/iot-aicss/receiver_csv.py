#!/usr/bin/env python3
"""
Receptor mínimo do sensor: recebe o JSON do ESP32 em POST /ocorrencias,
mostra no console e grava em CSV. Serve para testar o sensor sem subir a API completa.
"""

import csv
import json
import math
import os
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CSV_PATH = Path(os.getenv("SENSOR_CSV_PATH", str(Path(__file__).resolve().parent / "leituras_iot.csv")))
MAX_BODY_BYTES = 64 * 1024
_CSV_LOCK = threading.Lock()
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
HEADERS = [
    "criado_em",
    "dispositivo_id",
    "tipo",
    "metrica",
    "valor",
    "gas_co",
    "temperatura_c",
    "umidade_pct",
    "status_local",
    "relato",
]


# Mesmos limiares do firmware e da API (índice de gases, escala da base real).
LIMIARES = {"gas_voc": (830.0, 1140.0), "gas_co": (1010.0, 1280.0)}


def classificar(metrica: str, valor: float) -> str:
    atencao, critico = LIMIARES.get(metrica, LIMIARES["gas_voc"])
    if valor >= critico:
        return "critico"
    if valor >= atencao:
        return "atencao"
    return "normal"


def csv_seguro(valor):
    """Evita CSV/formula injection ao abrir o arquivo no Excel."""
    if isinstance(valor, str) and valor.startswith(_FORMULA_PREFIXES):
        return "'" + valor
    return valor


def garantir_csv() -> None:
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "csv": str(CSV_PATH)})
            return
        self._send(404, {"erro": "rota nao encontrada"})

    def do_POST(self):
        if self.path != "/ocorrencias":
            self._send(404, {"erro": "rota nao encontrada"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY_BYTES:
            self._send(413 if length > MAX_BODY_BYTES else 400, {"erro": "Content-Length invalido ou excessivo"})
            return
        raw = self.rfile.read(length).decode("utf-8", "replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._send(400, {"erro": "JSON invalido"})
            return
        if not isinstance(data, dict):
            self._send(400, {"erro": "O corpo deve ser um objeto JSON"})
            return

        for req_field in ("dispositivo_id", "metrica", "valor"):
            if data.get(req_field) is None:
                self._send(400, {"erro": f"Campo obrigatorio ausente: {req_field}"})
                return
        try:
            valor = float(data["valor"])
            if isinstance(data["valor"], bool) or not math.isfinite(valor):
                raise ValueError
        except (TypeError, ValueError):
            self._send(400, {"erro": "Campo valor deve ser numerico"})
            return

        status = classificar(str(data["metrica"]), valor)
        criado_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {
            "criado_em": criado_em,
            "dispositivo_id": data["dispositivo_id"],
            "tipo": data.get("tipo") or data.get("tipo_dispositivo", "esp32"),
            "metrica": data["metrica"],
            "valor": valor,
            "gas_co": data.get("gas_co", ""),
            "temperatura_c": data.get("temperatura_c", ""),
            "umidade_pct": data.get("umidade_pct", ""),
            "status_local": status,
            "relato": data.get("relato", ""),
        }
        row = {k: csv_seguro(v) if isinstance(v, str) else v for k, v in row.items()}
        with _CSV_LOCK:
            garantir_csv()
            with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=HEADERS).writerow(row)

        print(f"[{criado_em}] {row['dispositivo_id']} | {row['metrica']}={row['valor']} | STATUS={status}")
        self._send(201, {"status_local": status, "criado_em": criado_em, "alerta": status != "normal"})

    def log_message(self, format, *args):
        return


def main():
    port = int(os.getenv("SENSOR_PORT", "8085"))
    garantir_csv()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Receptor do sensor ativo em http://127.0.0.1:{port} -> CSV: {CSV_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    main()
