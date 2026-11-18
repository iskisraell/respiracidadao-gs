# RespiraCidadão: FIAP Global Solution 2026.2

- **Turma:** `1TIAPZ1` (Tecnologia em Inteligência Artificial, Noturno - Paulista)
- **Grupo:** **Perceptron**
- **Integrantes:**
  - Giovanni Henrique Pereira Hessel (`RM 570574`)
  - Suellen Pereira da Silva (`RM 573862`)
  - Israel Carneiro de Toledo (`RM 573854`)
- **Tema CitizenTech:** Monitoramento comunitário de qualidade do ar, fumaça de queimadas e risco respiratório com IoT, API Serverless, Machine Learning, Redes Neurais e Cibersegurança (ODS 3, 10 e 11).

## Estrutura do Monorepo

```
respiracidadao-gs/
├── apps/
│   ├── api/                 # API REST unificada (FastAPI: 05 Python, 07 Cloud, 03 Cyber, 06 ML + 08 DL live inference)
│   └── web/                 # Frontend React + TypeScript com design tokens oficiais da FIAP
├── packages/
│   ├── iot-aicss/           # 02 AICSS: ESP32 (Wokwi) + MQ-2 + DHT22 + LEDs/Buzzer + receptor Python CSV
│   ├── cloud-serverless/    # 07 Cloud: AWS Lambda + RDS PostgreSQL + Hugging Face + simulador
│   ├── stats-r-python/      # 09 Statistical Computing: inferência, testes de hipótese e regressões sobre o UCI Air Quality
│   ├── ml-modelling/        # 06 Machine Learning: comparação de modelos, tuning e feature importance (.ipynb + joblib)
│   ├── neural-networks/     # 08 Redes Neurais: MLP Baseline vs Regularizada (PyTorch, 8 etapas obrigatórias)
│   └── data-science-oracle/ # 04 Cognitive Data Science (standalone): 5 queries Oracle SQL (Inclusive Mobility Rover)
├── data/
│   ├── raw/                 # Base real UCI Air Quality (AirQualityUCI.csv)
│   └── processed/           # Base limpa e rotulada para treino e estatística
├── docs/                    # Documentos DOCX + PDF gerados com branding FIAP + roteiros de vídeo/pitch
└── deliverables/            # Pacotes .zip prontos para envio por disciplina
```

## Mapeamento por Disciplina

| # | Disciplina | Pasta / Módulo | Entregável Principal |
|---|---|---|---|
| 01 | AI Challenges | `docs/01-ai-challenges/` | Dossiê integrador + roteiro vídeo <= 7 min |
| 02 | AI Computer Systems & Sensors | `packages/iot-aicss/` | Firmware ESP32/Wokwi + receptor Python + CSV + PDF |
| 03 | Cognitive Cybersecurity | `apps/api/app/security.py` + `docs/03-cognitive-cybersecurity/` | Rate limit, Auth, SHA-256, logs + PDF <= 15 pág. + pitch |
| 04 | Cognitive Data Science | `packages/data-science-oracle/` | 5 consultas Oracle SQL (SurveyMonkey individual) |
| 05 | Computational Thinking with Python | `apps/api/` | FastAPI (`POST`/`GET`), CSV, indicadores, 3 cenários + PDF |
| 06 | Machine Learning & Modelling | `packages/ml-modelling/` | Notebook `.ipynb` + modelo + slides + pitch |
| 07 | Cloud Computing & Serviços Cognitivos | `packages/cloud-serverless/` | Lambda, SQL RDS, simulador, prints + vídeo <= 5 min |
| 08 | Redes Neurais e Deep Learning | `packages/neural-networks/` | Notebook `.ipynb` (8 etapas) + curvas + vídeo demo |
| 09 | Statistical Computing with R & Python | `packages/stats-r-python/` | `air_quality_clean.csv` + script `.py` + relatório `.pdf` |

## Como Rodar Localmente

### 1. Backend API (porta `8000`)
```bash
export RESPIRA_API_KEY="<defina-uma-chave-local>"   # protege DELETE /ocorrencias (X-API-Key); sem ela a rota fica bloqueada (503)
.venv/bin/uvicorn apps.api.app.main:app --reload --port 8000
```

### 2. Frontend React + TypeScript (porta `5173`)
```bash
cd apps/web
npm install
npm run dev
```

Para gerar o bundle de produção do frontend: `cd apps/web && npm run build`.

### 3. Testes Automatizados
```bash
.venv/bin/pytest -v apps/api/tests/test_api.py
.venv/bin/python packages/cloud-serverless/teste_local.py
```

### 4. Regenerar Documentos e Pacotes (`docs/` e `deliverables/`)
```bash
.venv/bin/python docs/build_diagrams_and_slides.py   # diagrama UML + slides do 06
.venv/bin/python docs/build_fiap_docs.py             # DOCX + PDF com branding FIAP
.venv/bin/python docs/package_deliverables.py        # 9 pacotes .zip em deliverables/
```
Os números dos documentos vêm de `packages/*/artifacts/*.json` (estatística, ML e redes neurais).
