#!/usr/bin/env python3
"""
Faz o papel do sensor: manda leituras para a função na nuvem (ou para servidor_local.py).

  --cenario normal    ar bom o tempo todo
  --cenario queimada  o ar piora a cada leitura até ficar ruim, com relatos de quem está perto
"""

import argparse
import json
import os
import random
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Índices de gases, na mesma escala do firmware. Atenção a partir de 830, ruim a partir de 1140.
CENARIOS = {
    "normal": {"inicio": 700.0, "passo": 5.0, "relatos": []},
    "queimada": {
        "inicio": 760.0,
        "passo": 120.0,
        "relatos": [
            None,
            "Cheiro leve de queimada vindo do terreno ao lado.",
            None,
            "Fumaça de queimada no portão, crianças tossindo.",
        ],
    },
}

LUGARES = {
    "escola": ("esp32-escola-zona-norte", -23.4892, -46.6208),
    "ubs": ("esp32-ubs-vila-maria", -23.5122, -46.5917),
    "praca": ("esp32-centro-01", -23.5505, -46.6333),
}


def enviar(url, payload, tempo_limite=30):
    req = urllib.request.Request(
        url.rstrip("/") + "/ocorrencias",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "RespiraCidadao-Sensor/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=tempo_limite) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read().decode("utf-8", "replace")
    except Exception as erro:
        return None, str(erro)


def main():
    p = argparse.ArgumentParser(description="Sensor simulado do RespiraCidadão")
    p.add_argument("--url", default=os.environ.get("FUNCTION_URL", "http://127.0.0.1:8099"))
    p.add_argument("--cenario", default="queimada", choices=list(CENARIOS))
    p.add_argument("--lugar", default="escola", choices=list(LUGARES))
    p.add_argument("--leituras", type=int, default=5)
    p.add_argument("--intervalo", type=float, default=0.5)
    args = p.parse_args()

    cen = CENARIOS[args.cenario]
    dispositivo, lat, lon = LUGARES[args.lugar]
    print(f"Sensor {dispositivo} -> {args.url.rstrip('/')}/ocorrencias ({args.cenario})")

    for i in range(args.leituras):
        gas = round(cen["inicio"] + cen["passo"] * i + random.uniform(-15, 15), 1)
        payload = {
            "dispositivo_id": dispositivo,
            "tipo_dispositivo": "esp32",
            "latitude": lat,
            "longitude": lon,
            "metrica": "gas_voc",
            "valor": gas,
            "gas_co": round(gas * 0.85 + 330 + random.uniform(-20, 20), 1),
            "temperatura_c": round(22 + i * 2 + random.uniform(-1, 1), 1),
            "umidade_pct": round(55 - i * 4 + random.uniform(-2, 2), 1),
            "medido_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        relato = cen["relatos"][i] if i < len(cen["relatos"]) else None
        if relato:
            payload["relato"] = relato
        status, resp = enviar(args.url, payload)
        if isinstance(resp, dict):
            extra = f" | relato lido como {resp['sentimento']}" if resp.get("sentimento") else ""
            alerta = "  << ALERTA" if resp.get("alerta") else ""
            print(f"[{i + 1}/{args.leituras}] gases {gas:7.1f} -> HTTP {status} nível {resp.get('nivel_risco')}{extra}{alerta}")
        else:
            print(f"[{i + 1}/{args.leituras}] gases {gas:7.1f} -> HTTP {status} {resp}")
        if i < args.leituras - 1:
            time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
