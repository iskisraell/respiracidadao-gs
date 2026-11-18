#!/usr/bin/env python3
"""
Gera todos os documentos oficiais FIAP (DOCX + PDF) usando skills/fiap-doc/scripts/generate.py
com dados reais dos artefatos do projeto e validacao automatica contra travessoes (em-dash e en-dash).
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
JSON_DIR = DOCS_DIR / "json_sources"
JSON_DIR.mkdir(parents=True, exist_ok=True)

_FIAP_GEN_CANDIDATES = [
    Path(os.environ["FIAP_DOC_GENERATOR"]) if os.environ.get("FIAP_DOC_GENERATOR") else None,
    Path("/home/agent/.t3/worktrees/fleet/t3-c6e26525-b98cac6896f353a6/skills/fiap-doc/scripts/generate.py"),
    Path.home() / ".agents" / "skills" / "fiap-doc" / "scripts" / "generate.py",
    Path.home() / "projects" / "fleet" / "skills" / "fiap-doc" / "scripts" / "generate.py",
]
FIAP_GEN = next((c for c in _FIAP_GEN_CANDIDATES if c and c.exists()), _FIAP_GEN_CANDIDATES[1])
VENV_PY = str(ROOT / ".venv" / "bin" / "python")

INTEGRANTES = (
    "Giovanni Henrique Pereira Hessel (RM 570574)\n"
    "Suellen Pereira da Silva (RM 573862)\n"
    "Israel Carneiro de Toledo (RM 573854)"
)

STATS = json.loads((ROOT / "packages" / "stats-r-python" / "artifacts" / "stats_summary.json").read_text(encoding="utf-8"))
ML = json.loads((ROOT / "packages" / "ml-modelling" / "artifacts" / "ml_metrics.json").read_text(encoding="utf-8"))
NN = json.loads((ROOT / "packages" / "neural-networks" / "artifacts" / "nn_metrics.json").read_text(encoding="utf-8"))


def meta(materia: str):
    return [
        {"label": "Sala:", "value": "1TIAPZ1"},
        {"label": "Matéria:", "value": materia},
        {"label": "Grupo:", "value": "Perceptron"},
        {"label": "Integrantes:", "value": INTEGRANTES},
    ]


def assert_no_em_dash(obj, path="root"):
    if isinstance(obj, str):
        if "\u2014" in obj or "\u2013" in obj:
            raise ValueError(f"Em/en-dash proibido encontrado em {path}: {obj[:80]}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            assert_no_em_dash(item, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            assert_no_em_dash(v, f"{path}.{k}")


IMG_WIDTH_MM = {"06": 150, "08": 150, "09": 140}


def render_doc(doc_spec: dict):
    # Largura menor evita legenda de figura orfa na pagina seguinte (limite de quebra do gerador).
    img_w = IMG_WIDTH_MM.get(doc_spec["filename"][:2])
    if img_w:
        for section in doc_spec.get("sections", []):
            for img in section.get("images", []):
                img.setdefault("width", img_w)
    assert_no_em_dash(doc_spec, doc_spec["filename"])
    json_path = JSON_DIR / f"{doc_spec['filename']}.json"
    json_path.write_text(json.dumps(doc_spec, indent=2, ensure_ascii=False), encoding="utf-8")
    subprocess.run([VENV_PY, str(FIAP_GEN), str(json_path)], check=True)


def build_all():
    arch_png = str(DOCS_DIR / "assets" / "arquitetura_uml_respiracidadao.png")
    stats_charts = ROOT / "packages" / "stats-r-python" / "charts"
    ml_charts = ROOT / "packages" / "ml-modelling" / "charts"
    nn_charts = ROOT / "packages" / "neural-networks" / "charts"

    # 1) 01 - AI Challenges (Dossie Integrador)
    doc01 = {
        "title": "RESPIRACIDADÃO: DOSSIÊ INTEGRADOR",
        "subtitle": ["Plataforma CitizenTech de Monitoramento Respiratório e Queimadas", "Global Solution 2026.2"],
        "subtitle_note": "Documento integrador de arquitetura, evidências e gestão",
        "meta": meta("AI Challenges"),
        "output_dir": str(DOCS_DIR / "01-ai-challenges"),
        "filename": "01_RespiraCidadao_Dossie_Integrador",
        "sections": [
            {
                "title": "1. PROBLEMA, PÚBLICO E PROPOSTA DE SOLUÇÃO",
                "body": [
                    "Episódios de fumaça de queimadas e picos de monóxido de carbono (CO), benzeno e NO2 elevam internações respiratórias antes que boletins públicos emitam alertas.",
                    "O RespiraCidadão atende crianças em escolas públicas, idosos e pacientes com asma ou DPOC em periferias urbanas, operando com hardware acessível, interface de alto contraste e alerta sonoro local."
                ],
                "bullets": [
                    {"text": "ODS 3 (Saúde e Bem-Estar): alerta precoce contra crises respiratórias agudas.", "level": 0},
                    {"text": "ODS 10 (Redução das Desigualdades): cobertura comunitária de baixo custo em áreas sem estações oficiais.", "level": 0},
                    {"text": "ODS 11 (Cidades Sustentáveis): dados abertos e rastreáveis para defesa civil e escolas.", "level": 0},
                    {"text": "Referência à Live de Lançamento da GS: conectamos dados ambientais reais, inclusão e IA responsável aplicada a cidades resilientes.", "level": 0},
                ],
            },
            {
                "title": "2. ARQUITETURA INTEGRADA E CONEXÃO ENTRE DISCIPLINAS",
                "body": [
                    "Cada disciplina forma uma camada operacional única da solução, sem entregas isoladas."
                ],
                "images": [{"path": arch_png, "caption": "Figura 1: Arquitetura integrada e fluxo de dados do RespiraCidadão."}],
                "tables": [
                    {
                        "headers": ["Disciplina", "Papel no Fluxo Integrado", "Evidência Principal"],
                        "rows": [
                            ["02 AICSS", "Nó ESP32 com MQ-2 + DHT22, LEDs, buzzer e JSON HTTP", "sketch.ino + diagram.json + 3 cenários"],
                            ["05 Python API", "FastAPI valida JSON, classifica limiares e grava CSV/SQLite", "POST/GET /ocorrencias + 11 testes pytest"],
                            ["07 Cloud", "Lambda + Function URL (fora VPC), CloudWatch, HF Router e RDS", "lambda_function.py + tabela_ocorrencias.sql"],
                            ["03 Cybersecurity", "Rate Limit 429, sanitização XSS/CSV, X-API-Key e SHA-256", "security.py + trilha JSONL + LGPD"],
                            ["09 Estatística", "Base real UCI (N=6.941), testes Z, regressões linear e logística", "R2=90,25% múltipla; Acc=94,30% logística"],
                            ["06 ML Modelling", "Pipeline sem leakage comparando 5 modelos + RandomizedSearchCV", "Random Forest Tuned 89,06% (F1 89,22%)"],
                            ["08 Redes Neurais", "PyTorch MLP regularizada com BatchNorm, Dropout e EarlyStop", "Teste 89,64% com gap de overfit de 0,07%"],
                            ["Frontend React", "Painel unificado com tokens FIAP integrado ao /predict e IoT", "App React + TS conectado à API local"],
                        ],
                        "col_widths": [38, 84, 58],
                    }
                ],
            },
            {
                "title": "3. IMPLEMENTADO VS EVOLUÇÃO FUTURA E GESTÃO",
                "tables": [
                    {
                        "headers": ["Escopo", "Implementado nesta GS", "Evolução Futura"],
                        "rows": [
                            ["Hardware IoT", "Simulação Wokwi (MQ-2 ADC + DHT22 + 3 LEDs + buzzer) e envio HTTP", "Placa física ESP32 com energia solar e LoRaWAN"],
                            ["Nuvem e IA", "API FastAPI + Lambda/RDS SQL + HF Router com fallback local + RF + MLP", "Treino contínuo com dados CETESB/INPE e push WhatsApp"],
                            ["Segurança", "Rate limit, sanitização XSS/CSV, X-API-Key, SHA-256 e auditoria", "MFA federado para gestores de Defesa Civil e UBS"],
                        ],
                        "col_widths": [32, 76, 72],
                    }
                ],
                "body": [
                    "Gestão das entregas: dividimos o projeto em trilha IoT/Cloud/Segurança, trilha Estatística/ML/DL sobre a mesma base UCI e integração final no painel React e repositório único no GitHub.",
                    "Acessibilidade, LGPD e sustentabilidade: alerta sonoro em hardware para baixa visão, coleta sem CPF ou dados pessoais identificáveis, e execução de modelos compactos com baixo custo computacional."
                ],
            },
        ],
    }

    # 2) 02 - AICSS
    doc02 = {
        "title": "RESPIRACIDADÃO: SISTEMA IOT E SENSORES",
        "subtitle": ["Monitoramento Local de Fumaça e Microclima com ESP32", "GS 2026.2 - AI Computer Systems & Sensors"],
        "meta": meta("AI Computer Systems & Sensors"),
        "output_dir": str(DOCS_DIR / "02-ai-computer-systems-and-sensors"),
        "filename": "02_RespiraCidadao_AICSS_IoT",
        "sections": [
            {
                "title": "1. PROBLEMA, PÚBLICO E RELEVÂNCIA (ODS 3 E 11)",
                "body": [
                    "Comunidades periféricas e escolas ficam expostas a plumas de fumaça e gases tóxicos sem estações oficiais próximas. Um nó ESP32 de baixo custo fornece aviso visual e sonoro imediato no local e envia telemetria JSON estruturada para análise em nuvem."
                ],
            },
            {
                "title": "2. HARDWARE, SENSORES E CONTRATO JSON",
                "tables": [
                    {
                        "headers": ["Componente", "Pino", "Justificativa Técnica"],
                        "rows": [
                            ["Sensor MQ-2 (ADC Wokwi)", "GPIO 34", "Detecta fumaça e gases combustíveis de 0 a 400 ppm."],
                            ["Sensor DHT22", "GPIO 15", "Mede temperatura (°C) e umidade relativa (%) que modulam dispersão."],
                            ["LEDs Verde/Amarelo/Vermelho", "GPIO 26/27/14", "Sinalização visual imediata para normal, atenção e crítico."],
                            ["Buzzer Piezoelétrico", "GPIO 12", "Alerta sonoro de acessibilidade (180 ms atenção, 1800 Hz crítico)."],
                        ],
                        "col_widths": [55, 30, 95],
                    }
                ],
                "body": [
                    "Contrato JSON enviado via HTTP POST para /ocorrencias (alinhado com 05 Python e 07 Cloud): {dispositivo_id, tipo, latitude, longitude, metrica, valor, temperatura_c, umidade_pct, relato}."
                ],
            },
            {
                "title": "3. EVIDÊNCIA DOS 3 COMPORTAMENTOS E LIMITAÇÕES",
                "tables": [
                    {
                        "headers": ["Cenário", "Entrada (fumaca_ppm)", "Atuador Local", "Resposta API & CSV"],
                        "rows": [
                            ["1. Normal", "68,4 ppm | 23,5°C | 58%", "LED Verde | Buzzer mudo", "HTTP 201 | nivel_risco=normal | gravado CSV"],
                            ["2. Atenção", "168,0 ppm | 31,2°C | 34%", "LED Amarelo | Pulso 180ms", "HTTP 201 | nivel_risco=atencao | gravado CSV"],
                            ["3. Crítico", "312,5 ppm | 36,8°C | 21%", "LED Vermelho | Sirene 1800Hz", "HTTP 201 | nivel_risco=critico | alerta=True"],
                        ],
                        "col_widths": [28, 48, 52, 52],
                    }
                ],
                "body": [
                    "Implementado vs Simulado: firmware C++/Arduino, circuito Wokwi (diagram.json + libraries.txt), receptor CSV (receiver_csv.py) e script de teste (run_3_cenarios.py) foram implementados; a leitura química foi simulada via potenciômetro ADC no Wokwi.",
                    "Limitações: o sensor MQ-2 real requer pré-aquecimento de 24h e calibração Rs/R0 em campo, além de depender de Wi-Fi para o envio remoto."
                ],
            },
        ],
    }

    # 3) 03 - Cognitive Cybersecurity (max 15 pages)
    doc03 = {
        "title": "CONSULTORIA DE CIBERSEGURANÇA E LGPD",
        "subtitle": ["Avaliação de Riscos e Controles Funcionais do Protótipo RespiraCidadão", "GS 2026.2 - Cognitive Cybersecurity"],
        "meta": meta("Cognitive Cybersecurity"),
        "output_dir": str(DOCS_DIR / "03-cognitive-cybersecurity"),
        "filename": "03_RespiraCidadao_Cybersecurity",
        "sections": [
            {
                "title": "1. SOLUÇÃO CITIZENTECH E ARQUITETURA SIMPLIFICADA",
                "body": [
                    "Público-alvo único: crianças, idosos e escolas públicas vulneráveis a fumaça e poluentes. Problema principal: exposição respiratória sem alerta precoce.",
                    "Arquitetura de dados: Usuário/ESP32 -> Aplicação React + API FastAPI -> Banco SQLite/RDS PostgreSQL e CSV -> Modelo de IA (Random Forest, PyTorch MLP e Hugging Face)."
                ],
            },
            {
                "title": "2. SUPERFÍCIE DE ATAQUE EM 5 CAMADAS",
                "tables": [
                    {
                        "headers": ["Camada", "Ameaças Identificadas", "Impacto Direto"],
                        "rows": [
                            ["Usuários", "Uso indevido de endpoints administrativos e phishing", "Limpeza ou falsificação de alertas comunitários"],
                            ["Aplicação", "Stored XSS no campo relato e CSV Formula Injection", "Execução de script no painel ou planilhas abertas"],
                            ["API", "Flood de requisições (DoS) e spoofing de X-Forwarded-For", "Indisponibilidade do servidor de telemetria"],
                            ["Banco de Dados", "SQL Injection e adulteração silenciosa de leituras", "Perda de confiabilidade das métricas de risco"],
                            ["Modelo de IA", "Envenenamento de entrada com valores fora de faixa", "Falsos negativos críticos em alertas de saúde"],
                        ],
                        "col_widths": [35, 78, 67],
                    }
                ],
            },
            {
                "title": "3. MATRIZ DE RISCOS E CONTROLES DE SEGURANÇA",
                "tables": [
                    {
                        "headers": ["Risco", "Prob. / Imp.", "Controles Propostos e Aplicados"],
                        "rows": [
                            ["R1. Flood HTTP na ingestão IoT", "Alta / Alto", "Rate Limiting Sliding Window (HTTP 429) e proxy confiável opt-in"],
                            ["R2. Acesso admin não autorizado", "Média / Crítico", "Header X-API-Key via HMAC (RESPIRA_API_KEY sem default hardcoded)"],
                            ["R3. XSS e CSV Injection em relatos", "Alta / Médio", "Sanitização HTML, controle de caracteres e prefixo seguro em CSV"],
                            ["R4. Adulteração de registro histórico", "Baixa / Alto", "Hash SHA-256 canônico verificado via GET /security/verify/{id}"],
                            ["R5. Manipulação de entradas da IA", "Média / Alto", "Validação estrita Pydantic (PredictIn) + fallback determinístico local"],
                            ["R6. Phishing / Engenharia Social", "Alta / Alto", "Canais oficiais assinados, MFA para gestores e treinamento"],
                        ],
                        "col_widths": [52, 28, 100],
                    }
                ],
            },
            {
                "title": "4. CONTROLES DE SEGURANÇA POR CATEGORIA E JUSTIFICATIVA",
                "body": [
                    "Justificativa técnica: priorizamos controles de baixo custo, testáveis em código e proporcionais ao risco de uma telemetria ambiental sem dados cadastrais. Itens marcados como Proposto dependem da conta de nuvem do grupo e entram na evolução futura.",
                ],
                "tables": [
                    {
                        "headers": ["Categoria", "Controle", "Status"],
                        "rows": [
                            ["Autenticação", "X-API-Key com hmac.compare_digest nas rotas administrativas; MFA e política de senhas fortes para gestores de Defesa Civil e UBS", "Chave implementada; MFA proposto"],
                            ["Firewall / WAF", "Rate Limiting por janela deslizante e CORS restrito na API; AWS WAF na Function URL e Security Group do RDS aberto só para a Lambda (porta 5432)", "Rate limit implementado; WAF e Security Group propostos"],
                            ["Backup e recuperação", "Snapshots automáticos do RDS PostgreSQL, cópia periódica do CSV/SQLite com hash SHA-256 e plano de restauração testado", "Proposto"],
                            ["Criptografia", "TLS em trânsito (Function URL HTTPS), criptografia em repouso do RDS com KMS e hash SHA-256 para integridade", "SHA-256 implementado; TLS e KMS propostos para produção"],
                            ["Monitoramento", "Trilha security_audit.jsonl na API, CloudWatch Logs com WARNING para payload inválido ou crítico e alarmes por taxa de HTTP 429/400", "Logs implementados; alarmes propostos"],
                        ],
                        "col_widths": [34, 100, 46],
                    }
                ],
            },
            {
                "title": "5. DEMONSTRAÇÃO OBRIGATÓRIA DE PROTEÇÕES FUNCIONANDO",
                "bullets": [
                    {"text": "Rate Limiting (HTTP 429): SlidingWindowRateLimiter bloqueou excedentes em teste automatizado (10x HTTP 201 seguidas de 2x HTTP 429) e registrou evento rate_limit_blocked.", "level": 0},
                    {"text": "Autenticação X-API-Key (HTTP 401/503): DELETE /ocorrencias bloqueia requisições sem chave válida com comparação em tempo constante (hmac.compare_digest).", "level": 0},
                    {"text": "Sanitização XSS e CSV: payloads com <script> são escapados antes da gravação e auditados em security_audit.jsonl.", "level": 0},
                    {"text": "Integridade SHA-256: GET /security/verify/{id} recalcula o hash canônico e detecta qualquer edição direta no arquivo SQLite.", "level": 0},
                    {"text": "Evidência automatizada: 11/11 testes em apps/api/tests/test_api.py validados com sucesso.", "level": 0},
                ],
            },
            {
                "title": "6. CONFORMIDADE LGPD E ENGENHARIA SOCIAL",
                "tables": [
                    {
                        "headers": ["Pergunta LGPD", "Resposta Objetiva no RespiraCidadão"],
                        "rows": [
                            ["Quais dados pessoais são tratados?", "Nenhum dado cadastral (sem nome, CPF ou e-mail). Apenas ID técnico da estação, coordenadas públicas aproximadas e relato opcional."],
                            ["Quais dados sensíveis podem existir?", "O campo relato pode conter menção espontânea de sintoma respiratório (dado de saúde se associado a pessoa física)."],
                            ["Quais proteções são aplicadas?", "Minimização na coleta, sanitização, acesso restrito por API Key, TLS em trânsito na nuvem e integridade SHA-256."],
                            ["Como o usuário é informado?", "Aviso explícito na interface orientando o cidadão a descrever o ambiente sem incluir nomes ou dados pessoais."],
                        ],
                        "col_widths": [62, 118],
                    }
                ],
                "body": [
                    "Cenário de Engenharia Social: atacante envia mensagem falsa no WhatsApp fingindo ser da Defesa Civil pedindo que diretores escolares instalem um aplicativo APK ou informem a chave de API do painel. Contramedidas: publicação exclusiva em domínio institucional HTTPS, treinamento da equipe escolar e autenticação multifator para contas administrativas."
                ],
            },
        ],
    }

    # 4) 05 - Computational Thinking with Python
    doc05 = {
        "title": "API REST EM PYTHON E PERSISTÊNCIA CSV",
        "subtitle": ["Serviço FastAPI Integrado ao ESP32 RespiraCidadão", "GS 2026.2 - Computational Thinking with Python"],
        "meta": meta("Computational Thinking with Python"),
        "output_dir": str(DOCS_DIR / "05-computational-thinking-with-python"),
        "filename": "05_RespiraCidadao_API_Python",
        "sections": [
            {
                "title": "1. PAPEL DA API NA SOLUÇÃO CITIZENTECH",
                "body": [
                    "A API REST em FastAPI recebe o JSON gerado pelo ESP32 (02 AICSS), valida campos obrigatórios e faixas numéricas com Pydantic, classifica o risco respiratório por função condicional, calcula indicadores agregados e persiste cada leitura em CSV (data/runtime/leituras.csv) e SQLite (ocorrencias.db)."
                ],
            },
            {
                "title": "2. ENDPOINTS, ESTRUTURA DE CÓDIGO E CONTRATO JSON",
                "tables": [
                    {
                        "headers": ["Rota", "Método", "Função Python / Lógica Aplicada"],
                        "rows": [
                            ["/health", "GET", "Verifica saúde da API, modelos carregados e dicionário THRESHOLDS."],
                            ["/ocorrencias", "POST", "Valida JSON (HTTP 400 se faltar campo), classifica e grava CSV + SQLite (HTTP 201)."],
                            ["/ocorrencias", "GET", "Consulta leituras filtradas por nivel_risco ou dispositivo_id."],
                            ["/indicadores", "GET", "Itera registros e calcula total, alertas, %, média, mínimo e máximo."],
                            ["/simulate", "POST", "Dispara os 3 cenários (normal, atencao, critico) ponta a ponta."],
                        ],
                        "col_widths": [36, 22, 122],
                    }
                ],
            },
            {
                "title": "3. OS 3 CENÁRIOS DE TESTE E LIMITAÇÕES",
                "tables": [
                    {
                        "headers": ["Cenário Testado", "Entrada POST (fumaca_ppm)", "Resposta HTTP e CSV"],
                        "rows": [
                            ["1. Normal", "valor=55.0 (esp32-01)", "201 | nivel_risco=normal | alerta=false | gravado no CSV"],
                            ["2. Atenção", "valor=165.0 (drone)", "201 | nivel_risco=atencao | alerta=true | gravado no CSV"],
                            ["3. Crítico + Validação", "valor=310.0 / payload incompleto", "201 (critico) / 400 (campos ausentes descartados)"],
                        ],
                        "col_widths": [42, 56, 82],
                    }
                ],
                "body": [
                    "Execução local: uvicorn app.main:app --app-dir apps/api --port 8000 e pytest -v apps/api/tests/test_api.py (11 testes aprovados).",
                    "Limitações: persistência CSV local não escala para milhares de escritas concorrentes sem migração para banco gerenciado (resolvida na camada 07 Cloud com RDS PostgreSQL). Relacionado ao ODS 3 e ODS 11."
                ],
            },
        ],
    }

    # 5) 06 - Machine Learning (Resumo PDF/DOCX complementar aos slides PPTX)
    doc06 = {
        "title": "MACHINE LEARNING & MODELLING",
        "subtitle": ["Relatório Técnico de Classificação de Risco Respiratório", "GS 2026.2 - Machine Learning and Modelling"],
        "meta": meta("Machine Learning & Modelling"),
        "output_dir": str(DOCS_DIR / "06-machine-learning-and-modelling"),
        "filename": "06_RespiraCidadao_ML_Resumo",
        "sections": [
            {
                "title": "1. BASE REAL, ALVO E PREVENÇÃO DE DATA LEAKAGE",
                "body": [
                    f"Utilizamos a base real UCI Air Quality ({STATS['dataset']['registros_limpos']} observações completas). O alvo multiclasse (normal, atencao, critico) deriva de CO(GT), variável removida das 11 entradas para eliminar vazamento.",
                    "Split estratificado 80/20 e StandardScaler encapsulado em Pipeline garantem que estatísticas de teste nunca influenciem o treino."
                ],
                "images": [{"path": str(ml_charts / "01_eda_classes_box.png"), "caption": "Figura 1: Proporção das classes (36,5%, 39,2% e 24,4%) e comportamento de C6H6(GT)."}],
            },
            {
                "title": "2. COMPARAÇÃO DE MODELOS, TUNING E FEATURE IMPORTANCE",
                "tables": [
                    {
                        "headers": ["Modelo", "Train Acc", "Test Acc", "Test F1-Macro", "Gap"],
                        "rows": [
                            [
                                r["modelo"],
                                f"{r['train_acc']*100:.2f}%",
                                f"{r['test_acc']*100:.2f}%",
                                f"{r['test_f1_macro']*100:.2f}%",
                                f"{r['gap_overfit']*100:.2f}%",
                            ]
                            for r in ML["comparacao_modelos"]
                        ],
                        "col_widths": [68, 28, 28, 30, 26],
                    }
                ],
                "images": [{"path": str(ml_charts / "02_confusao_feature_importance.png"), "caption": "Figura 2: Matriz de Confusão do Random Forest Otimizado e Importância das Variáveis."}],
                "body": [
                    f"O RandomForestClassifier otimizado com RandomizedSearchCV (CV=5, F1-Macro={ML['cv_f1_macro']:.4f}) atingiu {ML['teste_accuracy']*100:.2f}% de acurácia em teste, com apenas {ML['matriz_confusao'][0][2] + ML['matriz_confusao'][2][0]} confusão direta entre Normal e Crítico em {sum(sum(l) for l in ML['matriz_confusao'])} amostras de teste."
                ],
            },
        ],
    }

    # 6) 07 - Cloud Computing
    doc07 = {
        "title": "PLATAFORMAS COGNITIVAS & CLOUD SERVERLESS",
        "subtitle": ["Ingestão Serverless AWS Lambda, CloudWatch, Hugging Face e RDS PostgreSQL", "GS 2026.2 - Cloud Computing"],
        "meta": meta("Plataformas, Serviços Cognitivos & Cloud Computing"),
        "output_dir": str(DOCS_DIR / "07-plataformas-servicos-cognitivos-cloud"),
        "filename": "07_RespiraCidadao_Cloud_Serverless",
        "sections": [
            {
                "title": "1. CENÁRIO, LIMIARES E ARQUITETURA SERVERLESS",
                "body": [
                    "A camada serverless recebe ocorrências de campo (ESP32, drone ou app), grava telemetria e alertas no CloudWatch Logs, interpreta o relato cidadão via Hugging Face Router (cardiffnlp/twitter-xlm-roberta-base-sentiment) e persiste tudo no Amazon RDS PostgreSQL.",
                    "Requisito crítico AWS: a função Lambda permanece fora da VPC para acessar o endpoint externo da Hugging Face sem custo de NAT Gateway."
                ],
                "tables": [
                    {
                        "headers": ["Rota Lambda Function URL", "Comportamento Implementado"],
                        "rows": [
                            ["GET /health", "Retorna status da função, modelo HF configurado e flag ia_ativa."],
                            ["POST /ocorrencias", "Valida obrigatoriedade/tipo (400 + WARNING se inválido), classifica, consulta IA e grava no RDS (201)."],
                            ["GET /ocorrencias", "Lista últimas ocorrências persistidas ordenadas da mais recente à mais antiga."],
                        ],
                        "col_widths": [54, 126],
                    }
                ],
            },
            {
                "title": "2. RESILIÊNCIA DE IA, TESTE LOCAL E EVIDÊNCIAS AWS",
                "body": [
                    "A chamada à IA usa apenas urllib para https://router.huggingface.co/hf-inference/models/{modelo} com token em HF_TOKEN. Se houver timeout, ausência de token ou HTTP inesperado, a função registra WARNING e conclui a gravação no banco usando a regra local determinística.",
                    "Validação local automatizada: packages/cloud-serverless/teste_local.py executou 8/8 cenários com sucesso, além do simulador simulador_dispositivo.py em fluxo progressivo de queimada."
                ],
            },
            {
                "title": "3. IMPLEMENTADO LOCALMENTE VS PENDENTE NA CONTA AWS",
                "tables": [
                    {
                        "headers": ["Item exigido", "Situação", "Como concluir"],
                        "rows": [
                            ["Código da Lambda, SQL, simulador e README", "Implementado e validado localmente", "Entregues no pacote 07"],
                            ["Function URL e endpoint do RDS (sem senha)", "Pendente: exige o deploy na conta AWS do grupo", "Passo a passo no README do pacote"],
                            ["4 prints (variáveis, simulador, CloudWatch, SELECT no RDS)", "Pendente: gerados após o deploy", "Capturar durante o vídeo de até 5 min"],
                        ],
                        "col_widths": [64, 64, 52],
                    }
                ],
            },
        ],
    }

    # 7) 08 - Redes Neurais & Deep Learning (8 etapas completas)
    doc08 = {
        "title": "REDES NEURAIS ARTIFICIAIS & DEEP LEARNING",
        "subtitle": ["Classificador Neural AirQualityMLP em PyTorch para Risco Respiratório", "GS 2026.2 - Redes Neurais & Deep Learning"],
        "meta": meta("Redes Neurais Artificiais, Deep Learning e Algoritmos Genéticos"),
        "output_dir": str(DOCS_DIR / "08-redes-neurais-deep-learning-ag"),
        "filename": "08_RespiraCidadao_Redes_Neurais",
        "sections": [
            {
                "title": "1. ETAPAS 1 A 4: PROBLEMA, BASE REAL, SPLIT E ARQUITETURA MLP",
                "bullets": [
                    {"text": "Etapa 1 (Problema): prever o risco respiratório (normal, atencao, critico) a partir de 11 variáveis contínuas de sensores para antecipar alertas em escolas e UBS.", "level": 0},
                    {"text": "Etapa 2 (Dataset): UCI Air Quality real com 6.941 leituras limpas, sem dados sintéticos.", "level": 0},
                    {"text": "Etapa 3 (Preparação): split estratificado 70% treino (4.858), 15% validação (1.041) e 15% teste (1.042), com StandardScaler ajustado apenas no treino.", "level": 0},
                    {"text": "Etapa 4 (Justificativa MLP): dados tabulares pontuais com lacunas temporais tornam MLP mais rápida e adequada do que CNN (grade 2D) ou RNN (sequência contínua).", "level": 0},
                ],
            },
            {
                "title": "2. ETAPAS 5 A 7: TREINAMENTO, REGULARIZAÇÃO E AVALIAÇÃO",
                "tables": [
                    {
                        "headers": ["Experimento", "Épocas", "Train Acc", "Test Acc", "F1-Macro", "Gap Overfit"],
                        "rows": [
                            [
                                r["configuracao"],
                                str(r["epocas_executadas"]),
                                f"{r['train_acc']*100:.2f}%",
                                f"{r['test_acc']*100:.2f}%",
                                f"{r['test_f1_macro']*100:.2f}%",
                                f"{r['gap_overfit']*100:.2f}%",
                            ]
                            for r in NN["comparacao_experimentos"]
                        ],
                        "col_widths": [68, 18, 23, 23, 24, 24],
                    }
                ],
                "images": [
                    {"path": str(nn_charts / "01_curvas_treinamento.png"), "caption": "Figura 1: Evolução de Loss e Acurácia (Baseline MLP vs Regularized MLP)."},
                    {"path": str(nn_charts / "02_matriz_confusao_nn.png"), "caption": "Figura 2: Matriz de Confusão do modelo PyTorch no conjunto de teste."},
                ],
                "body": [
                    "A introdução de BatchNorm1d, Dropout (0,25) e weight decay (1e-4) derrubou o overfitting de 4,60% para apenas 0,07%, elevando a acurácia em teste para 89,64% (F1-Macro 89,85%) com zero erros graves entre Normal e Crítico. O Early Stopping (paciência de 8 épocas) restaura o melhor estado de validação, mas não chegou a interromper o treino dentro das 60 épocas."
                ],
            },
            {
                "title": "3. ETAPA 8: DEMONSTRAÇÃO NÃO VISTA, LIMITAÇÕES E LGPD",
                "tables": [
                    {
                        "headers": ["Cenário Não Visto", "Classe Predita", "Probabilidades (Normal / Atenção / Crítico)"],
                        "rows": [
                            [
                                d["cenario"],
                                d["classe_predita"].upper(),
                                f"{d['probabilidades']['normal']*100:.1f}% / {d['probabilidades']['atencao']*100:.1f}% / {d['probabilidades']['critico']*100:.1f}%",
                            ]
                            for d in NN["demonstracao_nao_vista"]
                        ],
                        "col_widths": [56, 36, 88],
                    }
                ],
                "body": [
                    "Integração ao produto: os pesos air_quality_mlp.pt rodam em tempo real no endpoint POST /predict e no painel React. Limitações: sensibilidade a deriva química exige recalibração periódica com dados locais brasileiros. Segurança e LGPD: apenas telemetria ambiental anônima entra na rede neural."
                ],
            },
        ],
    }

    # 8) 09 - Statistical Computing (Relatorio Estatistico Profissional)
    it2 = STATS["item_02_normal"]
    it3 = STATS["item_03_testes_hipotese"]
    it4 = STATS["item_04_regressao_simples"]
    it5 = STATS["item_05_regressao_multipla"]
    it6 = STATS["item_06_regressao_logistica"]

    doc09 = {
        "title": "RELATÓRIO ESTATÍSTICO DE QUALIDADE DO AR",
        "subtitle": ["Consultoria Analítica RespiraCidadão sobre Base Real UCI Air Quality", "GS 2026.2 - Statistical Computing with R & Python"],
        "meta": meta("Statistical Computing with R & Python"),
        "output_dir": str(DOCS_DIR / "09-statistical-computing-r-python"),
        "filename": "09_RespiraCidadao_Relatorio_Estatistico",
        "sections": [
            {
                "title": "1. BASE REAL E CONTEXTO CITIZENTECH",
                "body": [
                    f"Base selecionada: {STATS['dataset']['nome']}, com {STATS['dataset']['registros_brutos']} registros horários originais e {STATS['dataset']['registros_limpos']} observações válidas após remoção das falhas de sensor (-200).",
                    "Justificativa da base: dados horários reais de sensores de gás em área urbana, com CO, benzeno e NO2 medidos por analisadores de referência, o que permite avaliar sensores de baixo custo para o problema de alerta respiratório (ODS 3 e 11).",
                    f"Distribuição de risco por CO(GT): {STATS['dataset']['distribuicao_risco']['normal']} Normal (<1,5 mg/m³), {STATS['dataset']['distribuicao_risco']['atencao']} Atenção (1,5 a 3,0 mg/m³) e {STATS['dataset']['distribuicao_risco']['critico']} Crítico (>=3,0 mg/m³)."
                ],
            },
            {
                "title": "2. DISTRIBUIÇÃO NORMAL E TESTES DE HIPÓTESE (ITENS 02 E 03)",
                "tables": [
                    {
                        "headers": ["Item", "Métrica / Hipótese", "Resultado Numérico", "Classificação / Decisão"],
                        "rows": [
                            ["02a", "P(X < média) para CO(GT)", f"{it2['p_menor_media']*100:.2f}% (média={it2['media']})", it2["classificacao_a"]],
                            ["02b", "P(X > mediana) para CO(GT)", f"{it2['p_maior_mediana']*100:.2f}% (mediana={it2['mediana']})", it2["classificacao_b"]],
                            [
                                "03a",
                                "H1: mu_amostral < mu_pop (n=20, alpha=6%)",
                                f"x_bar={it3['teste_3a_unilateral_esquerda']['media_amostral']} | Z={it3['teste_3a_unilateral_esquerda']['z_calculado']} (crit {it3['teste_3a_unilateral_esquerda']['z_critico']}) | p={it3['teste_3a_unilateral_esquerda']['p_valor']}",
                                it3["teste_3a_unilateral_esquerda"]["decisao"],
                            ],
                            [
                                "03b",
                                "H1: mu_amostral > mu_pop (n=25, alpha=9%)",
                                f"x_bar={it3['teste_3b_unilateral_direita']['media_amostral']} | Z={it3['teste_3b_unilateral_direita']['z_calculado']} (crit {it3['teste_3b_unilateral_direita']['z_critico']}) | p={it3['teste_3b_unilateral_direita']['p_valor']}",
                                it3["teste_3b_unilateral_direita"]["decisao"],
                            ],
                        ],
                        "col_widths": [15, 58, 62, 45],
                    }
                ],
                "images": [{"path": str(stats_charts / "02_distribuicao_normal_co.png"), "caption": "Figura 1: Distribuição empírica vs curva Normal teórica de CO(GT)."}],
            },
            {
                "title": "3. ANÁLISE BIVARIADA E REGRESSÃO LINEAR SIMPLES (ITEM 04)",
                "body": [
                    f"Entre PT08.S1(CO) e CO(GT), a covariância é {it4['covariancia']} e a correlação de Pearson é r = {it4['pearson_r']} (forte correlação positiva, p < 0,0001).",
                    f"Equação: {it4['equacao']}. Adequação: R² = {it4['r2']*100:.2f}% e Teste F = {it4['teste_f']} (p < 0,0001). Previsão para sensor PT08.S1(CO) = 1350: {it4['previsao_exemplo']['co_previsto']} mg/m³ (nível crítico)."
                ],
                "images": [
                    {"path": str(stats_charts / "04_dispersao_regressao_simples.png"), "caption": "Figura 2: Dispersão, reta ajustada e ponto previsto."},
                    {"path": str(stats_charts / "04_correlacao_bivariada.png"), "caption": "Figura 3: Correlação linear bivariada por decis."},
                ],
            },
            {
                "title": "4. ANÁLISE MULTIVARIADA E REGRESSÃO MÚLTIPLA (ITEM 05)",
                "body": [
                    f"Explicando CO(GT) por PT08.S1(CO), C6H6(GT), NO2(GT) e Temperatura (T), o modelo alcança R² = {it5['r2']*100:.2f}% (R² ajustado = {it5['r2_ajustado']*100:.2f}%) e Teste F = {it5['teste_f']} (p < 0,0001).",
                    f"Equação ajustada: {it5['equacao']}.",
                    "Interpretação das correlações: C6H6(GT) (r=0.93), PT08.S1(CO) (r=0.877) e NO2(GT) (r=0.6738) acompanham CO(GT), enquanto a temperatura é praticamente independente (r=0.0183). A correlação de 0.8774 entre PT08.S1(CO) e C6H6(GT) indica colinearidade moderada entre sensores.",
                    f"Previsões multivariadas: cenário Atenção Urbana = {it5['previsoes'][0]['co_previsto']} mg/m³; cenário Crítico Queimada = {it5['previsoes'][1]['co_previsto']} mg/m³."
                ],
                "tables": [
                    {
                        "headers": ["Covariância", "CO(GT)", "PT08.S1(CO)", "C6H6(GT)", "NO2(GT)", "T"],
                        "rows": [
                            [nome] + [f"{it5['matriz_covariancia'][nome][col]:.4f}" for col in it5["matriz_covariancia"]]
                            for nome in it5["matriz_covariancia"]
                        ],
                        "col_widths": [32, 28, 32, 30, 30, 28],
                    }
                ],
                "images": [
                    {"path": str(stats_charts / "05_dispersao_multivariada.png"), "caption": "Figura 4: Dispersão multivariada das variáveis explicativas vs CO(GT)."},
                    {"path": str(stats_charts / "05_matriz_correlacao.png"), "caption": "Figura 5: Matriz de Correlação Linear de Pearson."},
                ],
            },
            {
                "title": "5. REGRESSÃO LOGÍSTICA BINÁRIA E RECOMENDAÇÕES (ITENS 06 E 07)",
                "body": [
                    f"Para classificar o evento crítico (CO >= 3,0 mg/m³), a regressão logística binária atingiu {it6['acuracia_teste']*100:.2f}% de acurácia em teste (Precisão={it6['precision_critico']*100:.2f}%, Recall={it6['recall_critico']*100:.2f}%, F1={it6['f1_critico']*100:.2f}%).",
                    f"Equação logit: {it6['equacao_logit']}.",
                    f"Matriz de confusão (teste, {sum(sum(l) for l in it6['matriz_confusao'])} casos): {it6['matriz_confusao'][0][0]} verdadeiros negativos, {it6['matriz_confusao'][1][1]} verdadeiros positivos, {it6['matriz_confusao'][0][1]} falsos alertas e {it6['matriz_confusao'][1][0]} alertas críticos não detectados. A acurácia alta com recall de {it6['recall_critico']*100:.2f}% mostra que o modelo captura a maior parte dos eventos críticos, mas ainda perde alguns, o que exige limiar conservador em produção.",
                    "Classificação de cenários com 4 variáveis: Atenção Urbana obteve P(Crítico)=1,85% (classe 0) e Crítico Queimada obteve P(Crítico)=99,61% (classe 1).",
                    "Conclusão executiva para tomada de decisão: combinar sensores óxido-metálicos de baixo custo (PT08.S1) com benzeno/NO2 eleva o poder explicativo de 76,92% para 90,25%, viabilizando alertas municipais confiáveis a baixo custo."
                ],
                "images": [{"path": str(stats_charts / "06_matriz_confusao_logistica.png"), "caption": "Figura 6: Matriz de Confusão da Regressão Logística Binária."}],
            },
        ],
    }

    for doc in [doc01, doc02, doc03, doc05, doc06, doc07, doc08, doc09]:
        render_doc(doc)
        print(f"[OK] Gerado DOCX + PDF: {doc['output_dir']}/{doc['filename']}.pdf")


if __name__ == "__main__":
    build_all()
