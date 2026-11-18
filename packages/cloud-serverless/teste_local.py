#!/usr/bin/env python3
"""Testa a função da nuvem sem RDS e sem token da IA."""

import json
import sys
from unittest.mock import patch


class _FakePg8000:
    pass


sys.modules.setdefault("pg8000", _FakePg8000)
import lambda_function  # noqa: E402

BANCO_MEMORIA = []


def fake_gravar(dados):
    novo_id = len(BANCO_MEMORIA) + 1
    registro = {"id": novo_id, **dados, "criado_em": "2026-11-18T00:00:00Z"}
    BANCO_MEMORIA.append(registro)
    return novo_id, registro["criado_em"]


def fake_listar(limite=20):
    return list(reversed(BANCO_MEMORIA[-limite:]))


def run_tests():
    with (
        patch.object(lambda_function, "gravar_ocorrencia", fake_gravar),
        patch.object(lambda_function, "listar_ocorrencias", fake_listar),
    ):
        # 1) Health
        r1 = lambda_function.lambda_handler({"requestContext": {"http": {"method": "GET"}}, "rawPath": "/health"}, None)
        assert r1["statusCode"] == 200

        # 2) 400 em payload incompleto
        r2 = lambda_function.lambda_handler(
            {
                "requestContext": {"http": {"method": "POST"}},
                "rawPath": "/ocorrencias",
                "body": json.dumps({"dispositivo_id": "esp32-x"}),
            },
            None,
        )
        assert r2["statusCode"] == 400

        # 3) 201 Cenario Normal
        r3 = lambda_function.lambda_handler(
            {
                "requestContext": {"http": {"method": "POST"}},
                "rawPath": "/ocorrencias",
                "body": json.dumps(
                    {
                        "dispositivo_id": "esp32-ubs-vila-maria",
                        "tipo_dispositivo": "esp32",
                        "metrica": "gas_voc",
                        "valor": 706.0,
                        "gas_co": 925.0,
                        "temperatura_c": 18.0,
                        "umidade_pct": 55.0,
                    }
                ),
            },
            None,
        )
        assert r3["statusCode"] == 201
        assert json.loads(r3["body"])["nivel_risco"] == "normal"

        # 4) 201 Cenario Critico
        r4 = lambda_function.lambda_handler(
            {
                "requestContext": {"http": {"method": "POST"}},
                "rawPath": "/ocorrencias",
                "body": json.dumps(
                    {
                        "dispositivo_id": "esp32-escola-zona-norte",
                        "tipo_dispositivo": "esp32",
                        "metrica": "gas_voc",
                        "valor": 1280.0,
                        "gas_co": 1383.0,
                        "relato": "Fumaca de queimada no portao, criancas tossindo",
                    }
                ),
            },
            None,
        )
        assert r4["statusCode"] == 201
        body4 = json.loads(r4["body"])
        assert body4["nivel_risco"] == "critico"
        assert body4["alerta"] is True
        assert body4["gas_co"] == 1383.0 and body4["temperatura_c"] is None

        # 5) GET /ocorrencias
        r5 = lambda_function.lambda_handler(
            {"requestContext": {"http": {"method": "GET"}}, "rawPath": "/ocorrencias"}, None
        )
        assert r5["statusCode"] == 200
        assert len(json.loads(r5["body"])["ocorrencias"]) == 2

        def post(corpo, **extra):
            evento = {
                "requestContext": {"http": {"method": "POST"}},
                "rawPath": "/ocorrencias",
                "body": corpo if isinstance(corpo, str) else json.dumps(corpo),
                **extra,
            }
            return lambda_function.lambda_handler(evento, None)

        base = {"dispositivo_id": "esp32-centro-01", "metrica": "gas_voc", "valor": 980}

        # 6) Entradas invalidas devem virar 400 (nunca 500) e nao gravar nada
        antes = len(BANCO_MEMORIA)
        assert post("isto nao e json")["statusCode"] == 400
        assert post("[1, 2, 3]")["statusCode"] == 400
        assert post({**base, "valor": "abc"})["statusCode"] == 400
        assert post({**base, "valor": "NaN"})["statusCode"] == 400
        assert post({**base, "latitude": "norte"})["statusCode"] == 400
        assert post({**base, "tipo_dispositivo": "drone"})["statusCode"] == 400
        assert post({**base, "gas_co": "alto"})["statusCode"] == 400
        assert post({**base, "dispositivo_id": "   "})["statusCode"] == 400
        assert post({**base, "relato": "x" * 501})["statusCode"] == 400  # igual à API: rejeita, não corta
        assert len(BANCO_MEMORIA) == antes
        sem_metrica = {k: v for k, v in base.items() if k != "metrica"}
        assert post(sem_metrica)["statusCode"] == 201  # metrica padrão gas_voc, igual à API

        # 7) Falha/resposta estranha da IA nao derruba a ingestao
        class _Resp:
            def __init__(self, conteudo):
                self.conteudo = conteudo

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return self.conteudo

        for conteudo in (b'{"error": "Model is loading"}', b'["texto"]', b"nao-json"):
            with patch.object(lambda_function, "HF_TOKEN", "token-fake"), patch.object(
                lambda_function.urllib.request, "urlopen", lambda *a, **k: _Resp(conteudo)
            ):
                r = post({**base, "relato": "Fumaca forte"})
            assert r["statusCode"] == 201, r
            assert json.loads(r["body"])["sentimento"] is None

        # 8) medido_em invalido nao quebra; body base64 (Function URL) e aceito
        assert post({**base, "medido_em": "ontem a noite"})["statusCode"] == 201
        import base64

        r = post(base64.b64encode(json.dumps(base).encode()).decode(), isBase64Encoded=True)
        assert r["statusCode"] == 201

        print("CLOUD LAMBDA LOCAL TESTS PASSED (8/8)")


if __name__ == "__main__":
    run_tests()
