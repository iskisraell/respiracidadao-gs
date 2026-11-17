#!/usr/bin/env python3
"""
Simulador de dispositivo RespiraCidadao (ESP32 / Drone) para AWS Lambda Function URL ou servidor local.
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

CENARIOS = {
    "normal": {
        "metrica": "fumaca_ppm",
        "inicio": 55.0,
        "passo": 4.0,
        "ruido": 6.0,
        "relatos": [
            "Ar limpo na regiao da Avenida Paulista, sem odor de fumaca.",
            "Visibilidade normal ao redor da escola municipal.",
        ],
    },
    "queimada": {
        "metrica": "fumaca_ppm",
        "inicio": 95.0,
        "passo": 48.0,
        "ruido": 10.0,
        "relatos": [
            "Cheiro leve de queimada vindo da zona norte.",
            "Neblina seca e irritacao leve na garganta dos moradores.",
            "Fumaca densa de queimada, criancas tossindo perto da UBS.",
        ],
    },
    "urbano_critico": {
        "metrica": "co_mg_m3",
        "inicio": 3.0,
        "passo": 1.8,
        "ruido": 0.4,
        "relatos": [
            "Trafego intenso no corredor de onibus.",
            "Ar pesado, relato de tontura e falta de ar em idosos.",
        ],
    },
}

PONTOS = [
    ("esp32-respira-01", -23.5641, -46.6524),
    ("esp32-respira-02", -23.5505, -46.6333),
    ("drone-respira-03", -23.4892, -46.6208),
]


def enviar(url, payload, tempo_limite=30):
    corpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url.rstrip("/") + "/ocorrencias",
        data=corpo,
        headers={"Content-Type": "application/json", "User-Agent": "RespiraCidadao-Simulador/1.0"},
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
    p = argparse.ArgumentParser(description="Simulador ESP32/Drone - RespiraCidadao")
    p.add_argument("--url", default=os.environ.get("FUNCTION_URL", "http://127.0.0.1:8099"))
    p.add_argument("--cenario", default="queimada", choices=list(CENARIOS))
    p.add_argument("--tipo", default="esp32", choices=["esp32", "drone", "app"])
    p.add_argument("--leituras", type=int, default=6)
    p.add_argument("--intervalo", type=float, default=0.5)
    args = p.parse_args()

    cen = CENARIOS[args.cenario]
    candidatos = [pt for pt in PONTOS if pt[0].startswith(args.tipo)] or PONTOS
    dispositivo, lat, lon = random.choice(candidatos)
    valor = cen["inicio"]

    print(f"Dispositivo : {dispositivo} ({args.tipo})")
    print(f"Cenario     : {args.cenario} / metrica {cen['metrica']}")
    print(f"Destino     : {args.url.rstrip('/')}/ocorrencias")
    print("-" * 72)

    for i in range(1, args.leituras + 1):
        leitura = round(max(0.0, valor + random.uniform(-cen["ruido"], cen["ruido"])), 1)
        payload = {
            "dispositivo_id": dispositivo,
            "tipo_dispositivo": args.tipo,
            "latitude": round(lat + random.uniform(-0.001, 0.001), 6),
            "longitude": round(lon + random.uniform(-0.001, 0.001), 6),
            "metrica": cen["metrica"],
            "valor": leitura,
            "relato": cen["relatos"][min(i - 1, len(cen["relatos"]) - 1)],
            "medido_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        status, resp = enviar(args.url, payload)
        print(f"[{i:02d}/{args.leituras}] POST {cen['metrica']}={leitura} -> HTTP {status}")
        if isinstance(resp, dict):
            print(
                f"         id={resp.get('id')} risco={resp.get('nivel_risco')} "
                f"sentimento={resp.get('sentimento')} confianca={resp.get('confianca')}"
                + ("  << ALERTA" if resp.get("alerta") else "")
            )
        else:
            print(f"         resposta: {resp}")
        valor += cen["passo"]
        if i < args.leituras:
            time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
