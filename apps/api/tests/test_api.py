import csv
import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("RESPIRA_DATA_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("RATE_LIMIT_MAX_REQUESTS", "10")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SEC", "60")
    monkeypatch.setenv("RESPIRA_API_KEY", "test-only-key")

    api_dir = Path(__file__).resolve().parents[1]
    if str(api_dir) not in sys.path:
        sys.path.insert(0, str(api_dir))

    import app.security as sec_mod
    import app.main as main_mod

    importlib.reload(sec_mod)
    importlib.reload(main_mod)
    main_mod.rate_limiter.reset()
    with TestClient(main_mod.app) as c:
        yield c, main_mod, tmp_path / "runtime"


def test_health(client):
    c, _, _ = client
    resp = c.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "gas_voc" in body["limiares"]


def test_validation_returns_400_on_missing_fields(client):
    c, _, _ = client
    resp = c.post("/ocorrencias", json={"dispositivo_id": "esp32-test"})
    assert resp.status_code == 400
    assert "erro" in resp.json()


def test_three_scenarios_and_csv_sqlite_persistence(client):
    c, _, runtime_dir = client
    payloads = [
        {
            "dispositivo_id": "esp32-01",
            "tipo": "esp32",
            "metrica": "gas_voc",
            "valor": 700.0, "gas_co": 920.0,
            "temperatura_c": 22.0,
            "umidade_pct": 60.0,
            "relato": "Ar limpo na estação.",
        },
        {
            "dispositivo_id": "esp32-02",
            "tipo_dispositivo": "drone",
            "metrica": "gas_voc",
            "valor": 980.0, "gas_co": 1120.0,
            "temperatura_c": 30.0,
            "umidade_pct": 35.0,
            "relato": "Cheiro de fumaça e neblina.",
        },
        {
            "dispositivo_id": "esp32-03",
            "tipo": "esp32",
            "metrica": "gas_voc",
            "valor": 1300.0, "gas_co": 1390.0,
            "temperatura_c": 37.5,
            "umidade_pct": 19.0,
            "relato": "Fumaça densa de queimada, tosse na escola <script>alert(1)</script>",
        },
    ]

    expected_risks = ["normal", "atencao", "critico"]
    expected_alerts = [False, True, True]
    ids = []
    for p, risk, alert in zip(payloads, expected_risks, expected_alerts):
        r = c.post("/ocorrencias", json=p)
        assert r.status_code == 201
        data = r.json()
        assert data["nivel_risco"] == risk
        assert data["alerta"] is alert
        assert len(data["hash_integridade"]) == 64
        ids.append(data["id"])

    # XSS sanitized on 3rd record
    listed = c.get("/ocorrencias").json()
    assert len(listed) == 3
    crit = [item for item in listed if item["id"] == ids[2]][0]
    assert "<script>" not in crit["relato"]
    assert "&lt;script&gt;" in crit["relato"]

    # CSV persistence check
    csv_path = runtime_dir / "leituras.csv"
    assert csv_path.exists()
    with csv_path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3

    # Indicators check
    ind = c.get("/indicadores").json()
    assert ind["total_leituras"] == 3
    assert ind["total_alertas"] == 2
    assert ind["max_valor"] == 1300.0

    # Integrity verification
    ver = c.get(f"/security/verify/{ids[0]}").json()
    assert ver["integro"] is True


def test_simulate_all_scenarios(client):
    c, _, _ = client
    resp = c.post("/simulate", json={"cenario": "todos", "tipo": "esp32"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["executados"] == 3


def test_api_key_protection_and_rate_limiter(client):
    c, main_mod, _ = client
    # Unauthorized DELETE
    r_unauth = c.delete("/ocorrencias")
    assert r_unauth.status_code == 401

    # Wrong key is rejected too
    assert c.delete("/ocorrencias", headers={"X-API-Key": "wrong"}).status_code == 401

    # Authorized DELETE
    r_auth = c.delete("/ocorrencias", headers={"X-API-Key": "test-only-key"})
    assert r_auth.status_code == 200

    # Rate limit test (limit is 10 per minute in fixture)
    main_mod.rate_limiter.reset()
    statuses = []
    for i in range(12):
        res = c.post(
            "/ocorrencias",
            json={
                "dispositivo_id": "esp32-burst",
                "metrica": "gas_voc",
                "valor": 40.0 + i,
            },
        )
        statuses.append(res.status_code)
    assert statuses.count(201) == 10
    assert statuses.count(429) == 2

    assert c.get("/security/audit").status_code == 401  # trilha tem IP: só com a chave
    audit = c.get("/security/audit", headers={"X-API-Key": "test-only-key"}).json()
    assert any(ev["event"] == "rate_limit_blocked" for ev in audit["events"])


def test_integrity_detects_tampering(client):
    import sqlite3

    c, _, runtime_dir = client
    rec = c.post(
        "/ocorrencias",
        json={"dispositivo_id": "esp32-hash", "metrica": "gas_voc", "valor": 300.0, "relato": "Fumaça forte"},
    ).json()
    assert c.get(f"/security/verify/{rec['id']}").json()["integro"] is True

    with sqlite3.connect(runtime_dir / "ocorrencias.db") as conn:
        conn.execute("UPDATE ocorrencias SET nivel_risco = 'normal', valor = 10 WHERE id = ?", (rec["id"],))
        conn.commit()
    ver = c.get(f"/security/verify/{rec['id']}").json()
    assert ver["integro"] is False
    assert ver["hash_armazenado"] != ver["hash_recalculado"]
    assert c.get("/security/verify/9999").status_code == 404

    # O selo cobre também temperatura e umidade.
    rec2 = c.post(
        "/ocorrencias",
        json={"dispositivo_id": "esp32-hash", "metrica": "gas_voc", "valor": 700.0, "temperatura_c": 20, "umidade_pct": 50},
    ).json()
    with sqlite3.connect(runtime_dir / "ocorrencias.db") as conn:
        conn.execute("UPDATE ocorrencias SET umidade_pct = 90 WHERE id = ?", (rec2["id"],))
        conn.commit()
    assert c.get(f"/security/verify/{rec2['id']}").json()["integro"] is False


def test_markup_in_identifiers_is_rejected_with_400(client):
    c, _, _ = client
    bad = {"dispositivo_id": "<img src=x onerror=alert(1)>", "metrica": "gas_voc", "valor": 10}
    assert c.post("/ocorrencias", json=bad).status_code == 400
    bad = {"dispositivo_id": "esp32-ok", "metrica": "<script>", "valor": 10}
    assert c.post("/ocorrencias", json=bad).status_code == 400
    assert c.get("/ocorrencias").json() == []


def test_spoofed_forwarded_header_does_not_bypass_rate_limit(client):
    c, _, _ = client
    codes = []
    for i in range(12):
        r = c.post(
            "/ocorrencias",
            json={"dispositivo_id": "esp32-spoof", "metrica": "gas_voc", "valor": 20.0},
            headers={"X-Forwarded-For": f"10.0.0.{i}"},
        )
        codes.append(r.status_code)
    assert codes.count(429) == 2


def test_csv_formula_injection_and_missing_value(client):
    c, _, runtime_dir = client
    r = c.post(
        "/ocorrencias",
        json={"dispositivo_id": "esp32-csv", "metrica": "gas_voc", "valor": 5, "relato": "=HYPERLINK(\"http://x\")"},
    )
    assert r.status_code == 201
    with (runtime_dir / "leituras.csv").open(encoding="utf-8") as f:
        row = list(csv.DictReader(f))[0]
    assert row["relato"].startswith("'=")
    # missing "valor" and "metrica" -> 400, nothing persisted
    assert c.post("/ocorrencias", json={"dispositivo_id": "esp32-x"}).status_code == 400
    assert len(c.get("/ocorrencias").json()) == 1


def test_indicators_cover_all_rows_not_only_last_1000(client):
    _, main_mod, _ = client
    for i in range(1005):
        main_mod.store.insert(
            {
                "dispositivo_id": "esp32-bulk", "tipo": "esp32", "latitude": None, "longitude": None,
                "metrica": "gas_voc", "valor": 10.0, "temperatura_c": None, "umidade_pct": None,
                "relato": "", "ia_sentimento": "sem_relato", "ia_confianca": None, "ia_fonte": "local-vazio",
                "nivel_risco": "normal", "alerta": False,
            }
        )
    assert main_mod.store.compute_indicators()["total_leituras"] == 1005


def test_admin_route_fails_closed_without_configured_key(tmp_path, monkeypatch):
    monkeypatch.setenv("RESPIRA_DATA_DIR", str(tmp_path / "runtime"))
    monkeypatch.delenv("RESPIRA_API_KEY", raising=False)
    import app.security as sec_mod
    import app.main as main_mod

    importlib.reload(sec_mod)
    importlib.reload(main_mod)
    with TestClient(main_mod.app) as c:
        assert c.delete("/ocorrencias", headers={"X-API-Key": ""}).status_code == 503
        assert c.delete("/ocorrencias", headers={"X-API-Key": "perceptron-fiap-2026"}).status_code == 503


def test_full_reading_gets_model_verdict(client):
    c, _, _ = client
    r = c.post("/ocorrencias", json={"dispositivo_id": "esp32-ia", "metrica": "gas_voc", "valor": 1280.0,
                                     "gas_co": 1383.0, "temperatura_c": 31.0, "umidade_pct": 34.0}).json()
    assert r["nivel_risco"] == "critico"
    assert r["ia_risco"] == "critico" and r["ia_risco_prob"] > 0.5
    partial = c.post("/ocorrencias", json={"dispositivo_id": "esp32-ia", "metrica": "gas_voc", "valor": 700.0}).json()
    assert partial["ia_risco"] is None


def test_predict_returns_three_verdicts(client):
    c, _, _ = client
    body = c.post("/predict", json={"gas_co": 925, "gas_voc": 706, "temperatura_c": 18, "umidade_pct": 55}).json()
    assert body["ml"]["classe"] == body["nn"]["classe"] == body["regra_local"]["classe"] == "normal"


def test_places_show_latest_reading_and_guidance(client):
    c, _, _ = client
    places = c.get("/locais").json()
    assert len(places) == 3 and all(p["nivel"] is None for p in places)
    c.post("/simulate", json={"cenario": "critico", "local_id": "escola-jardim-primavera"})
    escola = next(p for p in c.get("/locais").json() if p["id"] == "escola-jardim-primavera")
    assert escola["nivel"] == "critico"
    assert escola["orientacao"]["titulo"] == "Ar ruim agora"
    assert escola["ultima_leitura"]["ia_risco"] == "critico"
    assert len(escola["historico"]) == 1
    assert escola["ultima_leitura"]["tipo"] == "demo"
    assert c.post("/simulate", json={"cenario": "normal", "local_id": "nao-existe"}).status_code == 404


def test_relatos_are_sanitized_and_flag_urgency(client):
    c, _, _ = client
    r = c.post("/relatos", json={"local_id": "praca-da-se", "texto": "Fumaça forte <b>na praça</b>"})
    assert r.status_code == 201
    body = r.json()
    assert body["urgente"] is True and "<b>" not in body["texto"]
    assert c.post("/relatos", json={"local_id": "outro-lugar", "texto": "oi tudo bem"}).status_code == 404
    praca = next(p for p in c.get("/locais").json() if p["id"] == "praca-da-se")
    assert praca["relatos"][0]["id"] == body["id"]


def test_hourly_pattern_points_to_afternoon_window(client):
    c, _, _ = client
    body = c.get("/padrao-horario").json()
    assert len(body["horas"]) == 24
    janela = body["melhor_janela"]
    assert 11 <= janela["inicio"] <= 15
    assert janela["pior_hora"] in (8, 9, 17)
