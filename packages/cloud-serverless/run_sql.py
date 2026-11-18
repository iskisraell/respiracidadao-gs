#!/usr/bin/env python3
"""
Roda SQL no PostgreSQL da central, sem precisar instalar o psql.

  python3 run_sql.py tabela_ocorrencias.sql   # cria a tabela e mostra as consultas de conferência
  python3 run_sql.py --consultas              # só mostra as últimas leituras e o resumo por sensor

Lê DB_HOST, DB_PORT, DB_NAME, DB_USER e DB_PASSWORD do ambiente. DB_SSL=0 desliga o SSL (só para teste local).
"""

import os
import sys
from pathlib import Path

import pg8000.native

CONSULTAS = [
    ("Últimas leituras",
     "SELECT id, dispositivo_id, valor, gas_co, nivel_risco, sentimento, criado_em "
     "FROM ocorrencias ORDER BY id DESC LIMIT 10"),
    ("Resumo por sensor",
     "SELECT dispositivo_id, COUNT(*) AS leituras, ROUND(AVG(valor)::numeric, 1) AS media, "
     "MAX(valor) AS pico, SUM((nivel_risco = 'critico')::int) AS ruins "
     "FROM ocorrencias GROUP BY dispositivo_id ORDER BY ruins DESC"),
]


def comandos(sql: str):
    sem_comentarios = "\n".join(linha.split("--", 1)[0] for linha in sql.splitlines())
    return [c.strip() for c in sem_comentarios.split(";") if c.strip()]


def mostrar(conn, titulo, sql):
    linhas = conn.run(sql)
    print(f"\n{titulo}")
    if conn.columns:
        print("  " + " | ".join(c["name"] for c in conn.columns))
    for linha in linhas or []:
        print("  " + " | ".join(str(v) for v in linha))


def main():
    conn = pg8000.native.Connection(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        ssl_context=os.environ.get("DB_SSL", "1") != "0" or None,
    )
    try:
        if len(sys.argv) > 1 and sys.argv[1] != "--consultas":
            for cmd in comandos(Path(sys.argv[1]).read_text(encoding="utf-8")):
                if cmd.upper().startswith("SELECT"):
                    continue
                conn.run(cmd)
                print("ok:", cmd.splitlines()[0][:70])
        for titulo, sql in CONSULTAS:
            mostrar(conn, titulo, sql)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
