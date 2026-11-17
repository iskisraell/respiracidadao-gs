import csv
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .security import compute_record_hash

CSV_HEADERS = [
    "id",
    "dispositivo_id",
    "tipo",
    "latitude",
    "longitude",
    "metrica",
    "valor",
    "temperatura_c",
    "umidade_pct",
    "relato",
    "ia_sentimento",
    "ia_confianca",
    "ia_fonte",
    "nivel_risco",
    "alerta",
    "hash_integridade",
    "criado_em",
]


_CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_safe(value):
    """Neutralise spreadsheet formula injection (CSV injection) in text cells."""
    if isinstance(value, str) and value.startswith(_CSV_FORMULA_PREFIXES):
        return "'" + value
    return value


class OccurrenceStore:
    """Dual persistence: CSV (05 Computational Thinking with Python) + SQLite/PG schema (07 Cloud)."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "ocorrencias.db"
        self.csv_path = self.data_dir / "leituras.csv"
        self._csv_lock = threading.Lock()
        self._init_db()
        self._init_csv()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ocorrencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dispositivo_id TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    metrica TEXT NOT NULL,
                    valor REAL NOT NULL,
                    temperatura_c REAL,
                    umidade_pct REAL,
                    relato TEXT NOT NULL,
                    ia_sentimento TEXT NOT NULL,
                    ia_confianca REAL,
                    ia_fonte TEXT NOT NULL,
                    nivel_risco TEXT NOT NULL,
                    alerta INTEGER NOT NULL,
                    hash_integridade TEXT NOT NULL,
                    criado_em TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _init_csv(self) -> None:
        if not self.csv_path.exists():
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(CSV_HEADERS)

    def insert(self, data: dict) -> dict:
        criado_em = datetime.now(timezone.utc).isoformat()
        payload = {**data, "criado_em": criado_em}
        digest = compute_record_hash(payload)
        payload["hash_integridade"] = digest

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO ocorrencias (
                    dispositivo_id, tipo, latitude, longitude, metrica, valor,
                    temperatura_c, umidade_pct, relato, ia_sentimento, ia_confianca,
                    ia_fonte, nivel_risco, alerta, hash_integridade, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["dispositivo_id"],
                    payload["tipo"],
                    payload.get("latitude"),
                    payload.get("longitude"),
                    payload["metrica"],
                    float(payload["valor"]),
                    payload.get("temperatura_c"),
                    payload.get("umidade_pct"),
                    payload["relato"],
                    payload["ia_sentimento"],
                    payload.get("ia_confianca"),
                    payload["ia_fonte"],
                    payload["nivel_risco"],
                    1 if payload["alerta"] else 0,
                    digest,
                    criado_em,
                ),
            )
            record_id = int(cur.lastrowid)
            conn.commit()

        record = {"id": record_id, **payload}
        with self._csv_lock, self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow({k: _csv_safe(record.get(k, "")) if record.get(k) is not None else "" for k in CSV_HEADERS})
        return record

    def list_all(self, risco: Optional[str] = None, dispositivo_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        query = "SELECT * FROM ocorrencias WHERE 1=1"
        params: list = []
        if risco:
            query += " AND nivel_risco = ?"
            params.append(risco)
        if dispositivo_id:
            query += " AND dispositivo_id = ?"
            params.append(dispositivo_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, record_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM ocorrencias WHERE id = ?", (record_id,)).fetchone()
        return self._row_to_dict(row) if row else None

    def compute_indicators(self) -> Dict[str, object]:
        """Aggregates over the whole table (not just the latest N rows)."""
        with self._connect() as conn:
            total, alertas, media, vmax, vmin = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(alerta), 0), AVG(valor), MAX(valor), MIN(valor) FROM ocorrencias"
            ).fetchone()
            por_risco = {"normal": 0, "atencao": 0, "critico": 0}
            for risco, qtd in conn.execute("SELECT nivel_risco, COUNT(*) FROM ocorrencias GROUP BY nivel_risco"):
                por_risco[risco] = qtd
            por_disp = {
                d: qtd
                for d, qtd in conn.execute(
                    "SELECT dispositivo_id, COUNT(*) FROM ocorrencias GROUP BY dispositivo_id ORDER BY dispositivo_id"
                )
            }

        if not total:
            return {
                "total_leituras": 0,
                "total_alertas": 0,
                "pct_alertas": 0.0,
                "media_valor": 0.0,
                "max_valor": 0.0,
                "min_valor": 0.0,
                "por_risco": por_risco,
                "por_dispositivo": {},
            }
        return {
            "total_leituras": total,
            "total_alertas": int(alertas),
            "pct_alertas": round((alertas / total) * 100.0, 2),
            "media_valor": round(media, 2),
            "max_valor": round(vmax, 2),
            "min_valor": round(vmin, 2),
            "por_risco": por_risco,
            "por_dispositivo": por_disp,
        }

    def clear_all(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM ocorrencias")
            conn.commit()
        with self._csv_lock, self.csv_path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADERS)

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict:
        d = dict(row)
        d["alerta"] = bool(d["alerta"])
        return d
