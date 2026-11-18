#!/usr/bin/env python3
"""
Envia as 3 leituras que o sensor manda em cada nível, uma por lugar:

  UBS Vila Esperança       ar bom       luz verde, buzzer quieto
  Praça da Sé              ar carregado luz amarela, bipe curto
  Escola Jardim Primavera  ar ruim      luz vermelha, alarme a cada 3 s

Os números são índices dos sensores de gás na mesma escala da base real de 6.941 horas.

Uso:
  python run_3_cenarios.py                              # API em 127.0.0.1:8000
  python run_3_cenarios.py --url http://127.0.0.1:8085  # receptor_csv.py
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

CENARIOS = [
    {
        "nome": "Ar bom na UBS Vila Esperança",
        "luz": "verde, buzzer quieto",
        "payload": {
            "dispositivo_id": "esp32-ubs-vila-maria",
            "latitude": -23.5122, "longitude": -46.5917,
            "metrica": "gas_voc", "valor": 706.0, "gas_co": 925.0,
            "temperatura_c": 18.0, "umidade_pct": 55.0,
        },
    },
    {
        "nome": "Ar carregado na Praça da Sé",
        "luz": "amarela, bipe curto",
        "payload": {
            "dispositivo_id": "esp32-centro-01",
            "latitude": -23.5505, "longitude": -46.6333,
            "metrica": "gas_voc", "valor": 980.0, "gas_co": 1120.0,
            "temperatura_c": 24.0, "umidade_pct": 42.0,
        },
    },
    {
        "nome": "Ar ruim na Escola Jardim Primavera",
        "luz": "vermelha, alarme a cada 3 s",
        "payload": {
            "dispositivo_id": "esp32-escola-zona-norte",
            "latitude": -23.4892, "longitude": -46.6208,
            "metrica": "gas_voc", "valor": 1280.0, "gas_co": 1383.0,
            "temperatura_c": 31.0, "umidade_pct": 34.0,
        },
    },
]


def enviar(endpoint: str, payload: dict) -> dict:
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="endereço da API ou do receptor")
    endpoint = parser.parse_args().url.rstrip("/") + "/ocorrencias"
    falhas = 0
    for c in CENARIOS:
        p = c["payload"]
        print(f"\n{c['nome']}")
        print(f"  sensor  gases {p['valor']:.0f} | CO {p['gas_co']:.0f} | {p['temperatura_c']} °C | {p['umidade_pct']}%")
        print(f"  luz     {c['luz']}")
        try:
            r = enviar(endpoint, p)
        except urllib.error.HTTPError as err:
            print(f"  ERRO    HTTP {err.code}: {err.read().decode('utf-8', 'replace')}")
            falhas += 1
            continue
        except urllib.error.URLError as err:
            print(f"  ERRO    sem conexão com {endpoint}: {err.reason}")
            falhas += 1
            continue
        nivel = r.get("nivel_risco") or r.get("status_local")
        extra = f" | central: {r['ia_risco']} ({r['ia_risco_prob']:.0%})" if r.get("ia_risco") else ""
        print(f"  gravado nível {nivel}{extra}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
