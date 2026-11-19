# FIAP — Global Solution 2026.2 (2º Semestre)

- **Aluno:** Israel Carneiro de Toledo (`RM 573854`)
- **Curso / Turma:** Tecnologia em Inteligência Artificial (Noturno - Paulista) — `1TIAPZ` (`2026`)
- **Tema Integrador:** **Protótipo CitizenTech com Dados e IA para um Público Definido**
- **Prazo Oficial no Portal:** `19/11/2026 23:55:00` *(recomendação explícita em Python: priorizar envio até **17:00 de 19/11** para evitar sobrecarga)*
- **Status Atual (em 13/11/2026):** Todos os 9 entregáveis constam como **Não Entregue** e com apenas `573854 - ISRAEL CARNEIRO DE TOLEDO` listado em *Integrantes*.
- **Portal:** [`https://on.fiap.com.br/local/entregatrabalhos/`](https://on.fiap.com.br/local/entregatrabalhos/)

> **Observação sobre todas as disciplinas de `1TIAPZ`:** O filtro do portal lista 11 disciplinas no total. Além das 9 abaixo com entrega em `19/11/2026`, `Extensão` e `Formação Social e Sustentabilidade` não possuem nenhuma entrega cadastrada (nem pendente, nem entregue, nem avaliada).

---

## Mapa de Entregáveis (9 Disciplinas)

| # | Disciplina | Título no Portal | Tema / Escopo | Onde Entregar | Grupo | Formatos / Entregáveis Principais | Pasta |
|---|---|---|---|---|---|---|---|
| 01 | **AI Challenges** | `GS 2026-2 - AIC` | Vídeo integrador do projeto completo (capstone) | Portal (`id=28685`) | Até 3 | Link do vídeo no **YouTube (Não listado)**, máx. **7 min**, rosto visível, sem música de fundo, citando a live de lançamento | [01-ai-challenges](./01-ai-challenges/README.md) |
| 02 | **AI Computer Systems & Sensors** | `GS2026.2 - AICSS` | IoT / ESP32 (físico ou Wokwi) + sensores + atuador + JSON → servidor Python → CSV | Portal (`id=28651`) | Individual ou até 3 | Relatório com capa/arquitetura/evidências/ODS + código (ESP32 + servidor Python) + 3 comportamentos demonstrados | [02-ai-computer-systems-and-sensors](./02-ai-computer-systems-and-sensors/README.md) |
| 03 | **Cognitive Cybersecurity** | `Protótipo CitizenTech com Dados e IA` | Consultoria de segurança, superfície de ataque, riscos, LGPD e 1 controle funcional | Portal (`id=28360`) | Individual ou até 3 | **PDF** (máx. 15 páginas) + **Vídeo Pitch** (máx. 5 min) + evidências de **>= 1 proteção funcionando** | [03-cognitive-cybersecurity](./03-cognitive-cybersecurity/README.md) |
| 04 | **Cognitive Data Science** | `GS2026.2` | **STANDALONE (não é CitizenTech):** 5 consultas **Oracle SQL** (*Inclusive Mobility Rover*) | **SurveyMonkey** (`VQNNZZZ`) — **NÃO postar no portal** (`id=28907`) | Fazer em até 3; **entrega INDIVIDUAL** | 5 queries SQL Oracle com aliases exatos (script `CRIACAO_CARGA_ORACLE.sql` nas Apostilas) | [04-cognitive-data-science](./04-cognitive-data-science/README.md) |
| 05 | **Computational Thinking with Python** | `Protótipo CitizenTech com Dados e IA` | API REST (Flask/FastAPI) integrada ao JSON do AICSS + CSV + GET + indicador | Portal (`id=28270`) | Individual ou até 3 | Documentação + código Python (`POST`/`GET`, CSV, >=1 indicador) + 3 cenários de teste | [05-computational-thinking-with-python](./05-computational-thinking-with-python/README.md) |
| 06 | **Machine Learning & Modelling** | `GS2026.2 - Machine Learning and Modelling` | Comparação de >=2 modelos ML (regressão/classificação) + tuning + feature importance | Portal (`id=28649`) | Grupo CitizenTech | **Notebook (`.ipynb`)** + **Slides (PPT/PDF)** + **Vídeo Pitch** (máx. 5 min, YouTube não listado ou Drive) | [06-machine-learning-and-modelling](./06-machine-learning-and-modelling/README.md) |
| 07 | **Plataformas, Serviços Cognitivos & Cloud Computing** | `Computação Serverless` | AWS Lambda (Function URL) + RDS PostgreSQL (`ocorrencias`) + IA (HF ou Comprehend) + simulador | Portal (`id=28952`) | Grupo CitizenTech | URL Lambda + endpoint RDS + SQL + código Lambda & simulador + 4 prints + README + **Vídeo** (máx. 5 min). **Starter kit em `./07-.../starter/`** | [07-plataformas-servicos-cognitivos-cloud](./07-plataformas-servicos-cognitivos-cloud/README.md) |
| 08 | **Redes Neurais Artificiais, Deep Learning e Algoritmos Genéticos** | `GS 2026.2` | Rede Neural (MLP / CNN / RNN) + otimização/regularização + demonstração | Portal (`id=28276`) | Até 3 | **Notebook (`.ipynb`)** com 8 etapas + evidências/gráficos + documentação com capa + **Demonstração em vídeo** | [08-redes-neurais-deep-learning-ag](./08-redes-neurais-deep-learning-ag/README.md) |
| 09 | **STATISTICAL COMPUTING WITH R & PYTHON** | `GS 2026.2` | Inferência (Normal + 2 Testes de Hipótese) + Regressão Simples/Múltipla + Logística Binária | Portal (`id=28491`) — **sem links, arquivos direto no portal** | Individual, dupla ou trio | **Base real** (`.csv` ou `.xlsx`) + **Código** (`.py` ou `.r`) + **Relatório estatístico** (`.pdf`) | [09-statistical-computing-r-python](./09-statistical-computing-r-python/README.md) |

---

## Como Tudo Se Conecta (Arquitetura Integrada)

8 das 9 disciplinas compartilham **o mesmo problema, público-alvo e contexto CitizenTech** (e apenas **04 - Cognitive Data Science** é independente em Oracle SQL):

```
[02 AICSS: ESP32 / Wokwi (>=2 sensores + atuador)]
        │  JSON (ex.: dispositivo_id, tipo, gps, metrica, valor, relato)
        ├──────────────────────────────────────────────────────┐
        ▼                                                      ▼
[05 Python: API REST Flask/FastAPI]                  [07 Cloud: AWS Lambda + Function URL]
  • Valida, classifica, indicador                      • POST/GET /ocorrencias + CloudWatch
  • Persiste em CSV + GET                              • IA externa (HF / Comprehend)
                                                       • Persiste no RDS PostgreSQL
        │                                                      │
        └──────────────────┬───────────────────────────────────┘
                           ▼
        [Dados reais públicos + telemetria do cenário]
          ├──► [09 Statistical Computing]  Normal, Testes Hipótese (6%/9%), Regressões Linear/Logística
          ├──► [06 Machine Learning]       >=2 modelos clássicos + Grid/RandomSearch + Feature Importance
          └──► [08 Redes Neurais / DL]     MLP / CNN / RNN + Regularização + Tuning
                           │
                           ▼
        [03 Cognitive Cybersecurity]
          • Avalia superfície de ataque (Usuário, App, API, Banco, Modelo de IA)
          • Matriz >=5 riscos, LGPD, Engenharia Social + >=1 proteção implementada (ex.: Rate Limit / Auth / Hash / Log)
                           │
                           ▼
        [01 AI Challenges — Vídeo Integrador (<=7 min)]
          • Junta tudo: problema + ODS + live de lançamento + arquitetura/UML + demo + gestão + segurança/acessibilidade
```

---

## Alertas Críticos & Regras que Tiram Nota se Esquecer

1. **Cadastro de grupo no portal:** Se fizer em dupla/trio, confirmar que todos os integrantes constam na entrega (atualmente só o RM `573854` aparece em todas). Em várias disciplinas a entrega pede **capa com nome completo e RM de todos**.
2. **Cognitive Data Science (`04`):** Entrega é **INDIVIDUAL** no link SurveyMonkey (`https://pt.surveymonkey.com/r/VQNNZZZ`) — no portal está escrito *"Aqui não precisa postar nada!"*.
3. **Statistical Computing (`09`):**
   - **Proibido enviar links** — subir `.csv`/`.xlsx`, `.py`/`.r` e `.pdf` diretamente no portal (`-2,0` pontos de penalidade se cadastrar/entregar errado).
   - **Proibido dataset sintético/fictício** — precisa usar base real (IBGE, dados.gov.br, Kaggle, etc.).
4. **Cloud (`07`):**
   - A Lambda **não** pode estar dentro de VPC (precisa sair para a internet para chamar Hugging Face).
   - Se usar Hugging Face, o endpoint atual é `https://router.huggingface.co/hf-inference/models/{modelo}` (`api-inference.huggingface.co` retorna `410`).
   - Falha na API de IA **não** pode derrubar a ingestão.
5. **AI Challenges (`01`):**
   - Vídeo no YouTube **Não listado**, máx. **7 minutos**, **rosto visível** de quem narra, **SEM música de fundo**, e **citar as ideias/reflexões da live de lançamento** (vale também para o prêmio de melhor solução: camiseta + shape da GS 2026.2).
6. **Horário de envio:** Evitar deixar para `23:55` do dia `19/11` — o aviso de Python recomenda enviar até **17:00 de 19/11**.

---

## Plano de Execução Sugerido (Ordem de Dependências)

- [ ] **Passo 0 — Definir o Cenário CitizenTech Único** *(escolher problema real com dataset público disponível no IBGE/Kaggle/dados.gov.br E que combine com 2+ sensores IoT — ex.: enchente/alagamento urbano, qualidade do ar/fumaça/queimada, ilha de calor/seca agrícola, ruído/segurança urbana).*
- [ ] **Passo 1 — Entrega Rápida Independente (`04` Cognitive Data Science):** Baixar `CRIACAO_CARGA_ORACLE.sql` nas Apostilas, rodar no Oracle, validar as 5 queries e submeter individualmente no SurveyMonkey.
- [ ] **Passo 2 — Núcleo IoT + API + Cloud (`02` AICSS → `05` Python → `07` Cloud):** Alinhar o contrato JSON único entre ESP32/Wokwi (`02`), API Flask/FastAPI (`05`) e Lambda + RDS (`07`, adaptando o starter kit em `./07-plataformas-servicos-cognitivos-cloud/starter/`).
- [ ] **Passo 3 — Camada Analítica & IA (`09` Estatística + `06` ML + `08` Redes Neurais):** Usar a base pública real escolhida para o problema CitizenTech (e conectar ao cenário do grupo).
- [ ] **Passo 4 — Segurança & LGPD (`03` Cybersecurity):** Auditar a arquitetura já montada (API + RDS + IA), implementar >=1 controle real (ex.: rate limiting / auth / validação / log / hash) na API, produzir PDF <= 15 pág. + pitch <= 5 min.
- [ ] **Passo 5 — Vídeos & Empacotamento Final (`01` AI Challenges + vídeos de `03`, `06`, `07`, `08`):** Gravar os pitches/demos e o vídeo integrador de até 7 min, revisar todos os PDFs/capas/RMs e subir até **17:00 de 19/11/2026**.
