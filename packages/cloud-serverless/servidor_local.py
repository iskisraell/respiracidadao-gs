#!/usr/bin/env python3
"""
Executor local que emula AWS Lambda Function URL + RDS em SQLite para testes sem AWS.
"""

import logging
import os
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = Path(__file__).resolve().parent / "ocorrencias_local.db"


class _FakePg8000:
    @staticmethod
    def connect(**kwargs):
        raise RuntimeError("Local runner uses SQLite mock.")


sys.modules.setdefault("pg8000", _FakePg8000)
import lambda_function  # noqa: E402


def _init_sqlite():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ocorrencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_id TEXT NOT NULL,
                tipo_dispositivo TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                metrica TEXT NOT NULL,
                valor REAL NOT NULL,
                relato TEXT,
                sentimento TEXT,
                confianca REAL,
                nivel_risco TEXT NOT NULL,
                medido_em TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def _sqlite_gravar(dados):
    dados = {**dados, "medido_em": dados["medido_em"].isoformat()}
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO ocorrencias
                (dispositivo_id, tipo_dispositivo, latitude, longitude,
                 metrica, valor, relato, sentimento, confianca, nivel_risco, medido_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dados["dispositivo_id"],
                dados["tipo_dispositivo"],
                dados["latitude"],
                dados["longitude"],
                dados["metrica"],
                dados["valor"],
                dados["relato"],
                dados["sentimento"],
                dados["confianca"],
                dados["nivel_risco"],
                dados["medido_em"],
            ),
        )
        conn.commit()
        row = conn.execute("SELECT id, criado_em FROM ocorrencias WHERE id = ?", (cur.lastrowid,)).fetchone()
        return row[0], row[1]


def _sqlite_listar(limite=20):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM ocorrencias ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
        return [dict(r) for r in rows]


class LambdaLocalHandler(BaseHTTPRequestHandler):
    def _handle(self, method: str):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        event = {"requestContext": {"http": {"method": method}}, "rawPath": self.path, "body": body}
        with (
            patch.object(lambda_function, "gravar_ocorrencia", _sqlite_gravar),
            patch.object(lambda_function, "listar_ocorrencias", _sqlite_listar),
        ):
            res = lambda_function.lambda_handler(event, None)
        self.send_response(res["statusCode"])
        for k, v in res.get("headers", {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(res["body"].encode("utf-8"))

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def log_message(self, format, *args):
        return


def main():
    _init_sqlite()
    port = int(os.environ.get("CLOUD_LOCAL_PORT", "8099"))
    print(f"Lambda local (RespiraCidadao) em http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), LambdaLocalHandler).serve_forever()


if __name__ == "__main__":
    main()
