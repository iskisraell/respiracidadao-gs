#!/usr/bin/env python3
"""
Demonstra 3 comportamentos distintos do no ESP32 RespiraCidadao:
  1) Normal (fumaca_ppm=68.4 -> LED Verde, Buzzer desligado -> API normal -> CSV)
  2) Atencao (fumaca_ppm=168.0 -> LED Amarelo, Buzzer pulso curto -> API atencao -> CSV)
  3) Critico (fumaca_ppm=312.5 -> LED Vermelho, Buzzer continuo -> API critico -> CSV)

Uso:
  python run_3_cenarios.py --url http://127.0.0.1:8000
"""

import argparse
import json
import sys
import urllib.error
import urllib.request


SCENARIOS = [
    {
        "nome": "Comportamento 1 - Ar Limpo (NORMAL)",
        "atuador_esperado": "LED Verde ligado | Buzzer silencioso",
        "payload": {
            "dispositivo_id": "esp32-respira-01",
            "tipo": "esp32",
            "latitude": -23.5641,
            "longitude": -46.6524,
            "metrica": "fumaca_ppm",
            "valor": 68.4,
            "temperatura_c": 23.5,
            "umidade_pct": 58.0,
            "relato": "Ar limpo na regiao da Avenida Paulista.",
        },
    },
    {
        "nome": "Comportamento 2 - Fumaca Moderada (ATENCAO)",
        "atuador_esperado": "LED Amarelo ligado | Buzzer pulso 180ms",
        "payload": {
            "dispositivo_id": "esp32-respira-02",
            "tipo": "esp32",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "metrica": "fumaca_ppm",
            "valor": 168.0,
            "temperatura_c": 31.2,
            "umidade_pct": 34.0,
            "relato": "Cheiro forte de fumaca e neblina seca.",
        },
    },
    {
        "nome": "Comportamento 3 - Fumaca Densa (CRITICO)",
        "atuador_esperado": "LED Vermelho ligado | Buzzer alarme 1800Hz",
        "payload": {
            "dispositivo_id": "esp32-respira-03",
            "tipo": "esp32",
            "latitude": -23.4892,
            "longitude": -46.6208,
            "metrica": "fumaca_ppm",
            "valor": 312.5,
            "temperatura_c": 36.8,
            "umidade_pct": 21.0,
            "relato": "Fumaca intensa de queimada perto da escola.",
        },
    },
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="URL base da API")
    args = parser.parse_args()
    endpoint = args.url.rstrip("/") + "/ocorrencias"
    falhas = 0

    for sc in SCENARIOS:
        print("=" * 72)
        print(sc["nome"])
        print("Atuador local :", sc["atuador_esperado"])
        print("JSON enviado  :", json.dumps(sc["payload"], ensure_ascii=False))
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(sc["payload"], ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            print(f"HTTP {resp.status}     :", json.dumps(body, ensure_ascii=False))
        except urllib.error.HTTPError as err:
            print(f"HTTP {err.code}     :", err.read().decode("utf-8", "replace"))
            falhas += 1
        except urllib.error.URLError as err:
            print(f"ERRO de conexao com {endpoint}: {err.reason}")
            falhas += 1
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
