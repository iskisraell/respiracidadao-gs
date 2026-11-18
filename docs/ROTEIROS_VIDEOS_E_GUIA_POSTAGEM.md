# Guia de Vídeos, Slides e Postagem nos Portais FIAP (`1TIAPZ1` / Grupo Perceptron)

**Integrantes:**
- Giovanni Henrique Pereira Hessel (RM 570574)
- Suellen Pereira da Silva (RM 573862)
- Israel Carneiro de Toledo (RM 573854)

**Prazo oficial:** 19/11/2026 às 23:55 *(recomendação FIAP: enviar até 17:00)*.

---

## 1. Roteiro do Vídeo Integrador (`01 - AI Challenges`, máx. 7 min)

**Checklist técnico obrigatório antes de gravar:**
- YouTube **Não listado** (testar o link em aba anônima antes de colar no Portal).
- **Rosto visível** da pessoa que estiver narrando.
- **SEM música de fundo**.
- Primeira ou última tela exibindo **nomes completos e RMs** dos 3 integrantes.
- Apenas 1 integrante envia o link no Portal.

**Estrutura de fala sugerida (6 min 30 s):**
1. **0:00 a 0:50 | Problema, Público e Live de Lançamento:** Apresentar o grupo Perceptron e RMs na tela. Explicar que crianças em escolas, idosos e asmáticos ficam expostos a picos de fumaça e CO sem estações locais. Conectar com ODS 3, 10 e 11 e com as reflexões da live de lançamento da GS sobre IA responsável e dados acessíveis.
2. **0:50 a 2:10 | Arquitetura Integrada:** Mostrar `docs/assets/arquitetura_uml_respiracidadao.png`. Explicar como `02 AICSS` (ESP32), `05 Python` (FastAPI + CSV), `07 Cloud` (Lambda + CloudWatch + Hugging Face + RDS), `03 Cybersecurity` (Rate Limit, XSS, X-API-Key, SHA-256), `09 Estatística` (UCI `N=6.941`), `06 ML` (Random Forest 89,06%) e `08 Redes Neurais` (PyTorch MLP 89,64%) operam como um produto único.
3. **2:10 a 5:15 | Demonstração Ao Vivo:**
   - Mostrar o painel **RespiraCidadão** (`http://localhost:5173`), clicar em **Simular 3 Cenários** e apontar os registros `normal`, `atencao` e `critico` gravados em SQLite e CSV.
   - Abrir a aba **Predição IA (ML + MLP)**, testar `Queimada Urbana` e mostrar Random Forest e PyTorch concordando em `CRÍTICO`.
   - Abrir **Segurança & LGPD**, clicar em **Testar Sanitização XSS** e **Testar Rate Limiting (429)** e verificar um hash **SHA-256**.
   - Diferenciar o que está implementado (simulação Wokwi, API, Lambda local, modelos treinados, painel React) da evolução futura (placa física solar + calibração CETESB).
4. **5:15 a 6:30 | Gestão das Entregas e Fechamento:** Explicar a divisão em trilhas no GitHub, cuidados com acessibilidade (buzzer + alto contraste), privacidade LGPD (sem dados cadastrais) e encerrar com tela contendo nomes e RMs.

---

## 2. Roteiros dos Pitches Curtos (`03`, `06`, `07`, `08`)

- **03 Cognitive Cybersecurity (máx. 5 min):** Mostrar as 5 camadas de ataque, a matriz com 6 riscos, as respostas da LGPD, o cenário de phishing contra escolas e demonstrar ao vivo na aba Segurança o `HTTP 429`, a sanitização `<script>` e a verificação `SHA-256`.
- **06 Machine Learning (máx. 5 min):** Apresentar os slides `06_RespiraCidadao_ML_Slides.pptx`, enfatizar zero data leakage (`CO(GT)` fora de `X`), comparar os 5 algoritmos (Random Forest Tuned 89,06% / F1 89,22%) e demonstrar previsão ao vivo no notebook ou no `/predict`.
- **07 Cloud Serverless (máx. 5 min):** Mostrar o simulador `simulador_dispositivo.py` enviando leituras progressivas para a Function URL da Lambda (fora da VPC), logs chegando no CloudWatch (`WARNING` no crítico e 400), resposta da IA HF Router com fallback e consulta `SELECT` no RDS PostgreSQL + 4 prints.
- **08 Redes Neurais (Demo Funcional):** Mostrar as 8 etapas no notebook `respira_neural_network.ipynb`, a queda do gap de overfitting de `4,60%` para `0,07%` com `BatchNorm + Dropout(0.25) + weight decay` (`89,64%` em teste; o Early Stopping de paciência 8 não chegou a interromper as 60 épocas) e testar 3 cenários não vistos no `/predict`.

---

## 3. Mapa Rápido de Entrega por Disciplina (`deliverables/*.zip`)

| Disciplina | Modo de Entrega | Pacote / Arquivos Obrigatórios |
|---|---|---|
| `01 AIC` | Link YouTube Não Listado no Portal | Vídeo <= 7 min (usar `01_RespiraCidadao_Dossie_Integrador.pdf` como apoio) |
| `02 AICSS` | Upload no Portal (`deliverables/02-aicss-iot.zip`) | `02_RespiraCidadao_AICSS_IoT.pdf`, `sketch.ino`, `diagram.json`, `libraries.txt`, `receiver_csv.py`, `run_3_cenarios.py` |
| `03 Cyber` | Upload PDF + Link Vídeo no Portal (`deliverables/03-cognitive-cybersecurity.zip` reúne PDF, DOCX e evidências) | `03_RespiraCidadao_Cybersecurity.pdf` (<= 15 págs) + Vídeo Pitch <= 5 min |
| `04 Data Science` | **INDIVIDUAL** no SurveyMonkey `VQNNZZZ` (`deliverables/04-cognitive-data-science-oracle.zip` guarda as queries) | Cada integrante confere colunas em `CRIACAO_CARGA_ORACLE.sql` e cola as 5 queries |
| `05 Python` | Upload no Portal (`deliverables/05-computational-thinking-python.zip`) | `05_RespiraCidadao_API_Python.pdf` + código FastAPI (`apps/api/app/`) + testes |
| `06 ML` | Upload no Portal (`deliverables/06-machine-learning-modelling.zip`) + Vídeo | `respira_ml_modelling.ipynb`, `06_RespiraCidadao_ML_Slides.pptx`, `06_RespiraCidadao_ML_Resumo.pdf` + Vídeo <= 5 min |
| `07 Cloud` | Portal (`deliverables/07-cloud-serverless.zip`, URL Lambda, endpoint RDS, prints, vídeo) | `lambda_function.py`, `tabela_ocorrencias.sql`, `simulador_dispositivo.py`, `07_RespiraCidadao_Cloud_Serverless.pdf`, 4 prints AWS + Vídeo <= 5 min |
| `08 Redes Neurais` | Upload no Portal (`deliverables/08-redes-neurais-deep-learning.zip`) + Vídeo | `respira_neural_network.ipynb`, `08_RespiraCidadao_Redes_Neurais.pdf` + Vídeo Demo |
| `09 Estatística` | **UPLOAD DIRETO NO PORTAL (SEM LINKS!)**; arquivos de `deliverables/09-statistical-computing-upload-direto.zip` | `air_quality_clean.csv`, `analise_estatistica.py`, `09_RespiraCidadao_Relatorio_Estatistico.pdf` |
