#!/usr/bin/env python3
"""
Gera os documentos de entrega (DOCX + PDF) com o gerador fiap-doc, a partir dos números reais
dos artefatos e sem travessões (em-dash e en-dash).
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
    img_w = IMG_WIDTH_MM.get(doc_spec["filename"][:2])
    if img_w:
        for section in doc_spec.get("sections", []):
            for img in section.get("images", []):
                img.setdefault("width", img_w)
    assert_no_em_dash(doc_spec, doc_spec["filename"])
    json_path = JSON_DIR / f"{doc_spec['filename']}.json"
    json_path.write_text(json.dumps(doc_spec, indent=2, ensure_ascii=False), encoding="utf-8")
    subprocess.run([VENV_PY, str(DOCS_DIR / "fiap_gen.py"), str(FIAP_GEN), str(json_path)], check=True)


def pct(x, casas=1):
    return f"{x * 100:.{casas}f}".replace(".", ",") + "%"


def num(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


NIVEL = {"normal": "Bom", "atencao": "Carregado", "critico": "Ruim"}


def build_all():
    assets = DOCS_DIR / "assets"
    arch_png = str(assets / "arquitetura_uml_respiracidadao.png")
    stats_charts = ROOT / "packages" / "stats-r-python" / "charts"
    ml_charts = ROOT / "packages" / "ml-modelling" / "charts"
    nn_charts = ROOT / "packages" / "neural-networks" / "charts"
    wokwi = ROOT / "packages" / "iot-aicss" / "evidencias"

    regra, campo, lab = ML["comparacao_conjuntos"]
    nn_regra, nn_base, nn_reg = NN["comparacao_experimentos"]
    ml_teste = sum(sum(l) for l in ML["matriz_confusao"])
    nn_teste = sum(sum(l) for l in NN["matriz_confusao"])

    # 01 - AI Challenges
    doc01 = {
        "title": "RESPIRACIDADÃO",
        "subtitle": ["O ar perto de você, em uma frase", "Visão geral do produto"],
        "subtitle_note": "Problema, arquitetura, demonstração e o que vem depois",
        "meta": meta("AI Challenges"),
        "output_dir": str(DOCS_DIR / "01-ai-challenges"),
        "filename": "01_RespiraCidadao_Dossie_Integrador",
        "sections": [
            {
                "title": "1. O PROBLEMA E PARA QUEM",
                "body": [
                    "Uma diretora abre o celular às 7h40 e lê: \"Ar ruim perto da escola agora. Mantenha as janelas fechadas e deixe a educação física para depois do almoço.\" O RespiraCidadão existe para essa frase chegar a tempo e ser verdadeira.",
                    "Fumaça de queimada e trânsito pesado pioram crises de asma e DPOC. Quem sente primeiro são crianças, idosos e pacientes de UBS na periferia, onde quase não há estação oficial de medição. O boletim público, quando sai, é da cidade inteira e chega horas depois.",
                    "Nosso público são três pessoas: a coordenação de escola ou UBS, que decide se a atividade é ao ar livre; a família com criança, idoso ou alguém com asma, que quer saber se é hora de sair; e o vizinho que viu fumaça e quer avisar alguém.",
                ],
                "bullets": [
                    {"text": "ODS 3, saúde e bem-estar: aviso antes da crise respiratória.", "level": 0},
                    {"text": "ODS 10, redução das desigualdades: um sensor barato onde a estação oficial não chega.", "level": 0},
                    {"text": "ODS 11, cidades sustentáveis: dado aberto e conferível por bairro.", "level": 0},
                    {"text": "Do tema CitizenTech da live de lançamento, levamos a ideia de tecnologia que o cidadão comum entende e usa sem treinamento. Por isso o app fala de ar, lugar, horário e ação, nunca de modelo ou métrica.", "level": 0},
                ],
            },
            {
                "title": "2. COMO A INFORMAÇÃO CHEGA ATÉ A PESSOA",
                "body": [
                    "Um sensor na parede mede fumaça, monóxido, temperatura e umidade. Se o ar piora, a luz muda de cor e o alarme toca na hora, mesmo sem internet. A leitura vai para a central, que confere com um modelo treinado em 6.941 horas reais de medição e devolve o nível com uma porcentagem de confiança. O app mostra a cor, uma frase e o que fazer.",
                ],
                "images": [{"path": arch_png, "caption": "Figura 1: Caminho de uma leitura, do sensor ao app.", "width": 165}],
                "tables": [
                    {
                        "headers": ["Parte do produto", "O que faz", "Disciplina e evidência"],
                        "rows": [
                            ["Sensor", "Mede 4 coisas, acende a luz certa e envia a leitura em JSON", "02 AICSS: firmware, circuito Wokwi, 3 prints dos estados"],
                            ["Central (API)", "Recebe, valida, classifica, guarda em CSV e banco, responde ao app", "05 Python: FastAPI, 16 testes automáticos"],
                            ["Central na nuvem", "A mesma central sem servidor ligado: função + banco gerenciado", "07 Cloud: Lambda, PostgreSQL, script de publicação"],
                            ["Proteções", "Limite de envios, chave para apagar, texto limpo, selo de integridade", "03 Cybersecurity: testes que provam cada proteção"],
                            ["Modelo da central", f"Acerta {round(campo['accuracy'] * 100)} de cada 100 horas com as 4 medidas do sensor", "06 ML: 6 modelos comparados, Random Forest ajustada"],
                            ["Segunda opinião", f"Rede neural que confirma o veredito ({pct(NN['teste_accuracy'], 0)} no teste)", "08 Redes Neurais: 8 etapas em PyTorch"],
                            ["Base e limiares", "Mostra que as medidas do sensor explicam o monóxido real", f"09 Estatística: R² de {pct(STATS['item_05_regressao_multipla']['r2'])}"],
                        ],
                        "col_widths": [36, 76, 68],
                    }
                ],
            },
            {
                "title": "3. DEMONSTRAÇÃO",
                "body": [
                    "O app tem duas telas. \"Agora\" mostra cada lugar com sua cor, o que fazer, o melhor horário para atividade ao ar livre e o que os vizinhos estão contando. \"Como funciona\" explica o caminho da informação, deixa testar uma leitura e diz o que ainda não resolvemos.",
                ],
                "images": [
                    {"path": str(assets / "app_agora.png"), "caption": "Figura 2: Tela Agora com a escola em ar ruim e a central concordando com 93% de confiança.", "width": 160},
                    {"path": str(assets / "app_horario_relatos.png"), "caption": "Figura 3: Melhor horário calculado da base real e relato de vizinho marcado como urgente.", "width": 160},
                    {"path": str(wokwi / "wokwi_3_ar_ruim.png"), "caption": "Figura 4: O sensor no simulador Wokwi com o LED vermelho aceso.", "width": 160},
                ],
            },
            {
                "title": "4. O QUE FUNCIONA HOJE E O QUE VEM DEPOIS",
                "tables": [
                    {
                        "headers": ["Parte", "Funciona hoje", "Próximo passo"],
                        "rows": [
                            ["Sensor", "Circuito completo no Wokwi, regra de luz e alarme, envio JSON", "Placa física com bateria solar e rádio LoRa onde não há Wi-Fi"],
                            ["Central", "API local com modelo, histórico, relatos e padrão por hora", "Publicar na nuvem com o script pronto (falta só a conta AWS)"],
                            ["Modelo", "Treinado em base real italiana, testado em horas que nunca viu", "Recalibrar com algumas semanas ao lado de uma estação CETESB"],
                            ["Aviso", "App web no celular e no computador", "Notificação no WhatsApp quando o lugar favorito ficar vermelho"],
                        ],
                        "col_widths": [26, 80, 74],
                    }
                ],
                "body": [
                    "Gestão: dividimos o trabalho em três frentes que se encontram no mesmo contrato de dados. Uma cuidou do sensor e da nuvem, outra da estatística e dos modelos, e a terceira da central, do app e das proteções. Toda decisão ficou registrada num plano único no repositório, com o motivo ao lado.",
                ],
            },
            {
                "title": "5. ACESSIBILIDADE, SEGURANÇA, DADOS PESSOAIS E SUSTENTABILIDADE",
                "bullets": [
                    {"text": "Acessibilidade: cor sempre acompanhada de palavra (Bom, Carregado, Ruim), contraste alto, textos curtos e alarme sonoro no sensor para quem não está olhando a tela.", "level": 0},
                    {"text": "Segurança: limite de 30 envios por minuto por endereço, chave obrigatória para apagar dados, texto de relato limpo antes de gravar e selo digital em cada leitura.", "level": 0},
                    {"text": "Dados pessoais (LGPD): o relato não pede nome, telefone nem localização. Guardamos só o texto e o lugar escolhido.", "level": 0},
                    {"text": "Sustentabilidade: modelos pequenos que rodam numa máquina comum, sensor de baixo consumo e nuvem que só cobra quando recebe leitura.", "level": 0},
                ],
            },
        ],
    }

    # 02 - AI Computer Systems & Sensors
    doc02 = {
        "title": "RESPIRACIDADÃO: O SENSOR",
        "subtitle": ["Um ESP32 que avisa na hora, mesmo sem internet", "Sistema IoT com sensores e atuadores"],
        "meta": meta("AI Computer Systems & Sensors"),
        "output_dir": str(DOCS_DIR / "02-ai-computer-systems-and-sensors"),
        "filename": "02_RespiraCidadao_AICSS_IoT",
        "sections": [
            {
                "title": "1. O PROBLEMA E POR QUE UM SENSOR NO LUGAR",
                "body": [
                    "Escolas e UBS da periferia ficam longe das estações oficiais de qualidade do ar. Quando a fumaça chega, ninguém no prédio sabe até alguém começar a tossir. Um sensor pequeno na parede resolve a parte mais urgente: avisa quem está ali, na hora, com luz e som, e manda a leitura para a central do bairro.",
                    "ODS 3 (saúde e bem-estar) e ODS 11 (cidades sustentáveis).",
                ],
            },
            {
                "title": "2. O CIRCUITO",
                "tables": [
                    {
                        "headers": ["Peça", "Pino", "Por que está ali"],
                        "rows": [
                            ["Sensor de fumaça e gases (potenciômetro no Wokwi)", "GPIO 34", "Medida principal. Decide a cor da luz."],
                            ["Sensor de monóxido (potenciômetro no Wokwi)", "GPIO 35", "Segunda medida de gás, usada pela central."],
                            ["DHT22", "GPIO 15", "Temperatura e umidade. Ar quente e seco segura a fumaça perto do chão."],
                            ["LEDs verde, amarelo e vermelho (220 Ω)", "GPIO 26, 27, 14", "Mostram o nível para quem passa."],
                            ["Buzzer", "GPIO 25", "Bip curto em ar carregado, alarme longo em ar ruim. Serve a quem não está olhando."],
                        ],
                        "col_widths": [62, 30, 88],
                    }
                ],
                "body": [
                    "A regra da luz usa só a medida de fumaça e gases: abaixo de 830 fica verde, de 830 a 1140 amarelo, acima de 1140 vermelho. Escolhemos esses cortes na base real de 6.941 horas. Sozinha, a regra acerta 84 de cada 100 horas, e funciona sem rede.",
                    "A cada 3 segundos o ESP32 monta um JSON e envia por HTTP POST para a central: {dispositivo_id, tipo, latitude, longitude, metrica: \"gas_voc\", valor, gas_co, temperatura_c, umidade_pct}. É o mesmo contrato da API em Python e da função na nuvem. O sensor não manda relato; relato é coisa de pessoa.",
                ],
            },
            {
                "title": "3. OS TRÊS COMPORTAMENTOS",
                "tables": [
                    {
                        "headers": ["Situação", "Leitura", "No sensor", "Na central"],
                        "rows": [
                            ["Ar bom (UBS de manhã)", "706 / 925 / 18 / 55%", "LED verde, buzzer mudo", "201, Bom, 100% de confiança"],
                            ["Ar carregado (praça, fim de tarde)", "980 / 1120 / 24 / 42%", "LED amarelo, bip de 150 ms", "201, Carregado, 95%"],
                            ["Ar ruim (queimada perto da escola)", "1280 / 1383 / 31 / 34%", "LED vermelho, alarme de 1800 Hz", "201, Ruim, 93%"],
                        ],
                        "col_widths": [42, 52, 44, 42],
                    }
                ],
                "body": ["Leitura na ordem: fumaça e gases / monóxido / temperatura / umidade. Os prints abaixo são do simulador Wokwi rodando o firmware deste pacote."],
            },
            {
                "title": "4. PRINTS DO SIMULADOR",
                "images": [
                    {"path": str(wokwi / "wokwi_1_ar_bom.png"), "caption": "Figura 1: Ar bom. LED verde aceso e JSON no monitor serial.", "width": 150},
                    {"path": str(wokwi / "wokwi_2_ar_carregado.png"), "caption": "Figura 2: Ar carregado. LED amarelo.", "width": 150},
                    {"path": str(wokwi / "wokwi_3_ar_ruim.png"), "caption": "Figura 3: Ar ruim. LED vermelho e alarme.", "width": 150},
                ],
            },
            {
                "title": "5. O QUE É REAL E O QUE É SIMULADO",
                "bullets": [
                    {"text": "Real: firmware em C++, circuito do Wokwi (diagram.json), receptor Python que grava CSV (receiver_csv.py) e o script que reproduz os 3 cenários (run_3_cenarios.py), testado contra a API e contra o receptor.", "level": 0},
                    {"text": "Simulado: os dois sensores de gás são potenciômetros. Um sensor de verdade precisa de aquecimento e calibração ao lado de uma estação oficial antes de valer o número.", "level": 0},
                    {"text": "Limite do Wokwi gratuito: a simulação não alcança um servidor fora do navegador. Nesse caso o sensor imprime \"SEM REDE: alerta local ativo\" e continua acendendo a luz certa. É o comportamento que queremos numa queda de Wi-Fi.", "level": 0},
                ],
            },
        ],
    }

    # 03 - Cognitive Cybersecurity
    doc03 = {
        "title": "RESPIRACIDADÃO: SEGURANÇA E DADOS PESSOAIS",
        "subtitle": ["Onde o produto pode ser atacado e como se defende", "Consultoria de cibersegurança e LGPD"],
        "meta": meta("Cognitive Cybersecurity"),
        "output_dir": str(DOCS_DIR / "03-cognitive-cybersecurity"),
        "filename": "03_RespiraCidadao_Cybersecurity",
        "sections": [
            {
                "title": "1. A SOLUÇÃO EM UMA PÁGINA",
                "body": [
                    "O RespiraCidadão avisa escolas, UBS e famílias quando o ar perto delas piora. Público: crianças, idosos e pessoas com asma na periferia. Problema: exposição à fumaça sem aviso a tempo.",
                    "Caminho dos dados: sensor ESP32 ou pessoa no app, central (API FastAPI), banco (SQLite e CSV no local, PostgreSQL na nuvem) e modelos de IA que conferem cada leitura. Um alarme falso faz a escola cancelar aula à toa; um alarme perdido deixa criança respirando fumaça. As duas falhas custam caro, e é isso que estamos protegendo.",
                ],
            },
            {
                "title": "2. SUPERFÍCIE DE ATAQUE EM 5 CAMADAS",
                "tables": [
                    {
                        "headers": ["Camada", "Ameaça", "O que acontece se der certo"],
                        "rows": [
                            ["Usuários", "Mensagem falsa pedindo a chave de administração; relato falso em massa", "Alguém apaga o histórico ou cria pânico num bairro"],
                            ["Aplicação", "Script escondido no texto do relato; fórmula no CSV", "Código roda no navegador de quem lê ou na planilha de quem abre o CSV"],
                            ["API", "Enxurrada de envios; IP falso no cabeçalho para driblar o limite", "Central fora do ar justamente durante uma queimada"],
                            ["Banco", "Edição direta no arquivo; injeção de SQL", "Histórico adulterado sem ninguém perceber"],
                            ["Modelo de IA", "Leituras fora de faixa para enganar o modelo", "Modelo diz ar bom com fumaça de verdade"],
                        ],
                        "col_widths": [26, 80, 74],
                    }
                ],
            },
            {
                "title": "3. MATRIZ DE RISCOS",
                "tables": [
                    {
                        "headers": ["Risco", "Prob. / Impacto", "Controle"],
                        "rows": [
                            ["R1. Enxurrada de envios", "Alta / Alto", "Limite de 30 envios por minuto por endereço, resposta 429"],
                            ["R2. Apagar dados sem permissão", "Média / Crítico", "Chave X-API-Key comparada em tempo constante; sem chave configurada, a rota fica fechada"],
                            ["R3. Script ou fórmula em relato", "Alta / Médio", "Texto escapado antes de gravar; células de CSV que começam com = + - @ ganham prefixo"],
                            ["R4. Histórico adulterado", "Baixa / Alto", "Selo HMAC-SHA256 (chave RESPIRA_SEAL_KEY fora do banco) cobrindo todos os campos da leitura, conferido em GET /security/verify/{id}"],
                            ["R5. Leitura absurda para enganar o modelo", "Média / Alto", "Faixas válidas por campo (Pydantic); fora da faixa vira 400 e não chega ao modelo"],
                            ["R6. Engenharia social", "Alta / Alto", "Canal oficial único, treino da equipe e MFA para quem administra"],
                        ],
                        "col_widths": [50, 28, 102],
                    }
                ],
            },
            {
                "title": "4. CONTROLES POR CATEGORIA",
                "body": [
                    "Priorizamos o que dá para provar em código e custa pouco. O que depende da conta de nuvem está marcado como proposto.",
                ],
                "tables": [
                    {
                        "headers": ["Categoria", "Controle", "Situação"],
                        "rows": [
                            ["Autenticação", "Chave para rotas de administração; MFA para gestores de escola e UBS", "Chave feita; MFA proposto"],
                            ["Firewall / WAF", "Limite por endereço e CORS restrito; AWS WAF na URL da função e banco aceitando só a porta 5432", "Limite feito; WAF proposto"],
                            ["Backup", "Snapshot diário do PostgreSQL e cópia do CSV com o selo de cada linha", "Proposto"],
                            ["Criptografia", "HTTPS na URL da função, SSL obrigatório na conexão com o banco, disco do banco cifrado", "SSL feito no código; resto na publicação"],
                            ["Monitoramento", "Registro de eventos de segurança (security_audit.jsonl) e avisos no CloudWatch para leitura descartada", "Feito; alarmes propostos"],
                        ],
                        "col_widths": [30, 104, 46],
                    }
                ],
            },
            {
                "title": "5. PROTEÇÕES FUNCIONANDO",
                "body": [
                    "Cada proteção abaixo tem um teste automático em apps/api/tests/test_api.py. Os 16 testes passam.",
                ],
                "bullets": [
                    {"text": "Limite de envios: com limite de teste em 10, os envios 11 e 12 voltam 429 e o evento rate_limit_blocked vai para o registro.", "level": 0},
                    {"text": "IP falso: trocar o cabeçalho X-Forwarded-For não dribla o limite, porque a central só confia nele atrás de um proxy declarado.", "level": 0},
                    {"text": "Chave: DELETE /ocorrencias sem chave ou com chave errada volta 401. Sem chave configurada no servidor, volta 503.", "level": 0},
                    {"text": "Relato com <script>: gravado escapado. Valor \"=HYPERLINK(...)\" no CSV ganha prefixo e não vira fórmula.", "level": 0},
                    {"text": "Adulteração: editamos uma leitura direto no SQLite e GET /security/verify/{id} passou a responder integro=false.", "level": 0},
                ],
            },
            {
                "title": "6. LGPD E ENGENHARIA SOCIAL",
                "tables": [
                    {
                        "headers": ["Pergunta", "Resposta"],
                        "rows": [
                            ["Que dados pessoais tratamos?", "Nenhum cadastro. Leitura de sensor tem ID do aparelho e coordenada pública do prédio. Relato tem só texto e lugar."],
                            ["Pode haver dado sensível?", "Sim. Um relato como \"meu filho está com falta de ar\" fala de saúde. Por isso não pedimos nome nem localização da pessoa."],
                            ["Como protegemos?", "Coleta mínima, texto limpo, chave para apagar, SSL até o banco e selo de integridade."],
                            ["Como a pessoa sabe?", "O formulário diz \"Sem nome, sem localização sua. Só o texto.\" e a tela Como funciona explica o resto."],
                        ],
                        "col_widths": [50, 130],
                    }
                ],
                "body": [
                    "Cenário de engenharia social: chega no WhatsApp da diretora uma mensagem \"da Defesa Civil\" pedindo para instalar um aplicativo novo de alerta ou mandar a chave do painel. Contramedidas: o produto só existe num endereço HTTPS divulgado pela secretaria, a equipe aprende a desconfiar de pedido de chave por mensagem e contas de administração usam MFA.",
                ],
            },
        ],
    }

    # 05 - Computational Thinking with Python
    doc05 = {
        "title": "RESPIRACIDADÃO: A CENTRAL EM PYTHON",
        "subtitle": ["API que recebe o sensor, decide o nível e guarda o histórico", "FastAPI com persistência em CSV"],
        "meta": meta("Computational Thinking with Python"),
        "output_dir": str(DOCS_DIR / "05-computational-thinking-with-python"),
        "filename": "05_RespiraCidadao_API_Python",
        "sections": [
            {
                "title": "1. O QUE A CENTRAL FAZ",
                "body": [
                    "O sensor na escola só sabe acender uma luz. Quem guarda o histórico, confere com o modelo e responde ao app é a central. Ela recebe o JSON do ESP32 (o mesmo contrato do sensor), recusa o que vier incompleto, classifica o nível por uma função condicional, grava em CSV (data/runtime/leituras.csv) e em SQLite, e calcula indicadores.",
                    "Limiares em um dicionário: gas_voc atenção 830 e crítico 1140; gas_co atenção 1010 e crítico 1280. Os mesmos números do firmware e da função na nuvem.",
                ],
            },
            {
                "title": "2. ROTAS",
                "tables": [
                    {
                        "headers": ["Rota", "Método", "O que faz"],
                        "rows": [
                            ["/ocorrencias", "POST", "Valida com Pydantic (400 se faltar campo ou valor fora da faixa), classifica, grava CSV e SQLite, devolve 201"],
                            ["/ocorrencias", "GET", "Lista leituras, com filtro por nível ou por sensor"],
                            ["/indicadores", "GET", "Total, alertas, percentual de alerta, média, mínimo e máximo"],
                            ["/locais", "GET", "Cada lugar com a última leitura, o nível, a frase e o que fazer"],
                            ["/relatos", "POST e GET", "Relato de vizinho, limpo, com urgência detectada"],
                            ["/padrao-horario", "GET", "Risco por hora do dia e a melhor janela para atividade ao ar livre"],
                            ["/health", "GET", "Estado da central e dos modelos"],
                        ],
                        "col_widths": [34, 24, 122],
                    }
                ],
            },
            {
                "title": "3. TRÊS CENÁRIOS DE TESTE",
                "tables": [
                    {
                        "headers": ["Cenário", "Entrada", "Resposta"],
                        "rows": [
                            ["1. Ar bom na UBS", "gas_voc=706, gas_co=925, 18 °C, 55%", "201, nivel_risco=normal, gravado no CSV"],
                            ["2. Ar carregado na praça", "gas_voc=980, gas_co=1120, 24 °C, 42%", "201, nivel_risco=atencao, alerta=true"],
                            ["3. Ar ruim na escola", "gas_voc=1280, gas_co=1383, 31 °C, 34%", "201, nivel_risco=critico, alerta=true"],
                            ["Extra: JSON incompleto", "sem o campo valor", "400, nada gravado"],
                        ],
                        "col_widths": [44, 66, 70],
                    }
                ],
                "body": [
                    "Para rodar: uvicorn app.main:app --app-dir apps/api --port 8000. Os cenários do sensor rodam com python packages/iot-aicss/run_3_cenarios.py, e os 16 testes automáticos com pytest apps/api/tests.",
                    "Limitações: CSV é ótimo para abrir numa planilha e ruim para muitas escritas ao mesmo tempo. Para vários bairros, a central vai para a nuvem com PostgreSQL. A classificação por limiar não vê tendência; quem olha o histórico é o modelo da central.",
                    "ODS 3 e ODS 11.",
                ],
            },
        ],
    }

    # 06 - Machine Learning (resumo, junto dos slides)
    doc06 = {
        "title": "RESPIRACIDADÃO: O MODELO DA CENTRAL",
        "subtitle": ["Como a central decide se o ar está bom, carregado ou ruim", "Resumo técnico que acompanha os slides"],
        "meta": meta("Machine Learning & Modelling"),
        "output_dir": str(DOCS_DIR / "06-machine-learning-and-modelling"),
        "filename": "06_RespiraCidadao_ML_Resumo",
        "sections": [
            {
                "title": "1. DADOS E ALVO",
                "body": [
                    f"Base real UCI Air Quality: {STATS['dataset']['registros_brutos']} horas medidas numa cidade italiana, {STATS['dataset']['registros_limpos']} completas depois de tirar as falhas de sensor (-200).",
                    "O alvo é o nível do ar pelo monóxido medido em laboratório: abaixo de 1,5 mg/m³ bom, até 3,0 carregado, acima ruim. As entradas são só as 4 medidas que nosso ESP32 tem: dois sensores de gás, temperatura e umidade. O valor de laboratório nunca entra como entrada, então não há vazamento.",
                    "Separamos 80% para treino e 20% para teste antes de qualquer ajuste, com proporção de classes igual nos dois. A padronização fica dentro do Pipeline e só aprende com o treino.",
                ],
                "images": [{"path": str(ml_charts / "01_eda_classes_box.png"), "caption": "Figura 1: Quantas horas em cada nível e como a medida de gases se separa entre eles."}],
            },
            {
                "title": "2. SEIS MODELOS NO MESMO TESTE",
                "tables": [
                    {
                        "headers": ["Modelo", "Treino", "Teste", "F1 médio", "Diferença"],
                        "rows": [
                            [r["modelo"], pct(r["train_acc"]), pct(r["test_acc"]), pct(r["test_f1_macro"]), f"{r['gap_overfit'] * 100:+.1f} pp".replace(".", ",")]
                            for r in ML["comparacao_modelos"]
                        ],
                        "col_widths": [68, 26, 26, 30, 30],
                    }
                ],
                "body": [
                    f"A Random Forest sem ajuste decorou o treino (100%) e caiu no teste. Com busca aleatória de hiperparâmetros e validação cruzada em 5 partes (F1 médio de {num(ML['cv_f1_macro'], 3)}), ela ficou com {pct(ML['teste_accuracy'])} no teste e só 1,5 ponto de diferença para o treino.",
                    "A regressão logística ficou 2 horas à frente em 1.389. Na prática é empate. Ficamos com a floresta porque ela não supõe fronteira reta entre os níveis e mostra quanto cada medida pesa.",
                ],
                "images": [{"path": str(ml_charts / "02_confusao_feature_importance.png"), "caption": "Figura 2: Onde o modelo erra e quanto cada medida pesa."}],
            },
            {
                "title": "3. POR QUE SÓ AS MEDIDAS DO SENSOR",
                "tables": [
                    {
                        "headers": ["Opção", "Acerta de cada 100 horas", "Funciona num bairro?"],
                        "rows": [
                            ["Regra simples do sensor (sem internet)", f"{regra['accuracy'] * 100:.0f}", "Sim, até sem rede"],
                            ["Modelo com as 4 medidas do sensor", f"{campo['accuracy'] * 100:.0f}", "Sim"],
                            ["Modelo com 11 medidas de laboratório", f"{lab['accuracy'] * 100:.0f}", "Não. Exige equipamento de estação oficial"],
                            ["4 medidas, testado em meses mais recentes", f"{ML['split_temporal_accuracy'] * 100:.0f}", "É o número mais honesto para quem instala hoje"],
                        ],
                        "col_widths": [76, 44, 60],
                    }
                ],
                "body": [
                    f"Entre as {ml_teste} horas de teste, nenhuma hora de ar bom virou ar ruim e nenhuma de ar ruim virou bom. Os erros ficam entre níveis vizinhos.",
                ],
            },
            {
                "title": "4. APLICAÇÃO NO PRODUTO E LIMITES",
                "tables": [
                    {
                        "headers": ["Leitura nunca vista", "Veredito", "Certeza"],
                        "rows": [
                            [d["cenario"], NIVEL[d["classe_predita"]], pct(max(d["probabilidades"].values()), 0)]
                            for d in ML["demonstracao_nao_vista"]
                        ],
                        "col_widths": [90, 45, 45],
                    }
                ],
                "body": [
                    "A central roda o modelo a cada leitura e o app mostra \"A central conferiu e concorda: Ruim, com 93% de confiança.\" Quando discorda da luz do sensor, o app mostra os dois níveis e diz para seguir o mais cuidadoso.",
                    "Limite: dados de outro país e clima. Em cada bairro novo o sensor fica algumas semanas ao lado de uma estação oficial (CETESB) para recalibrar. Sensores de gás também envelhecem e precisam de troca.",
                ],
            },
        ],
    }

    # 07 - Cloud
    doc07 = {
        "title": "RESPIRACIDADÃO: A CENTRAL NA NUVEM",
        "subtitle": ["Função serverless, banco gerenciado e IA de texto", "AWS Lambda, CloudWatch, Hugging Face e RDS PostgreSQL"],
        "meta": meta("Plataformas, Serviços Cognitivos & Cloud Computing"),
        "output_dir": str(DOCS_DIR / "07-plataformas-servicos-cognitivos-cloud"),
        "filename": "07_RespiraCidadao_Cloud_Serverless",
        "sections": [
            {
                "title": "1. CENÁRIO E LIMIARES",
                "body": [
                    "Uma prefeitura não quer manter um servidor ligado em cada bairro. A central na nuvem só existe quando chega leitura: o sensor manda o JSON para uma URL, uma função Lambda valida, classifica, pede à IA de texto uma leitura do relato (quando houver) e grava no PostgreSQL. Tudo que dá errado vira aviso no CloudWatch.",
                    "Limiares: gas_voc atenção 830 e crítico 1140; gas_co atenção 1010 e crítico 1280. Tipos aceitos: esp32 e app. ODS 3 e ODS 11.",
                    "A função fica fora da VPC para alcançar a Hugging Face sem pagar NAT Gateway. O banco aceita conexão pública com senha e SSL obrigatório. Serve para demonstração; em produção o banco vai para rede privada.",
                ],
                "tables": [
                    {
                        "headers": ["Rota da Function URL", "Comportamento"],
                        "rows": [
                            ["GET /health", "Estado da função e se a IA de texto está ligada"],
                            ["POST /ocorrencias", "Valida campos e tipos (400 e WARNING no CloudWatch se inválido), classifica, chama a IA, grava no RDS e devolve 201"],
                            ["GET /ocorrencias", "Últimas leituras gravadas, da mais nova para a mais antiga"],
                        ],
                        "col_widths": [50, 130],
                    }
                ],
            },
            {
                "title": "2. IA DE TEXTO SEM DERRUBAR A GRAVAÇÃO",
                "body": [
                    "A função chama https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-xlm-roberta-base-sentiment com o token em HF_TOKEN, usando só urllib. Sem token, com timeout ou resposta estranha, ela registra WARNING e grava a leitura do mesmo jeito. Uma queimada não pode esperar a IA de texto voltar.",
                ],
            },
            {
                "title": "3. TESTADO SEM AWS",
                "bullets": [
                    {"text": "teste_local.py: 8 de 8 verificações passam: saúde da função, leitura bom e ruim gravadas, listagem, e recusa com 400 para JSON quebrado, valor não numérico, tipo de aparelho inválido e campo faltando, sem gravar nada.", "level": 0},
                    {"text": "Banco: rodamos tabela_ocorrencias.sql num PostgreSQL local, gravamos 3 leituras pelo próprio handler da Lambda e o GET devolveu as 3.", "level": 0},
                    {"text": "simulador_dispositivo.py --cenario queimada --lugar escola manda leituras que sobem até o vermelho, igual ao que a função vai receber.", "level": 0},
                ],
            },
            {
                "title": "4. O QUE FALTA E COMO FAZER",
                "body": [
                    "Não temos conta AWS ainda. Escrevemos deploy_aws.sh para que publicar seja um comando: ele cria o banco (db.t3.micro), roda a tabela, empacota e publica a função com a Function URL e imprime os comandos de teste. Funciona no AWS Academy Learner Lab (usa a LabRole) ou numa conta própria no nível gratuito.",
                ],
                "tables": [
                    {
                        "headers": ["Item exigido", "Situação", "Como concluir"],
                        "rows": [
                            ["Código da função, SQL, simulador, README", "Pronto e testado", "No pacote"],
                            ["URL da função e endpoint do RDS (sem senha)", "Sai no fim do deploy_aws.sh", "Copiar para o README"],
                            ["Print das variáveis de ambiente", "Depois do deploy", "Console Lambda, Configuração"],
                            ["Print do simulador enviando", "Depois do deploy", "Terminal com simulador_dispositivo.py"],
                            ["Print do CloudWatch", "Depois do deploy", "Grupo de logs da função"],
                            ["Print do SELECT no RDS", "Depois do deploy", "python run_sql.py --consultas"],
                        ],
                        "col_widths": [68, 50, 62],
                    }
                ],
            },
        ],
    }

    # 08 - Redes Neurais
    doc08 = {
        "title": "RESPIRACIDADÃO: A SEGUNDA OPINIÃO",
        "subtitle": ["Rede neural em PyTorch que confere o veredito da central", "As 8 etapas do projeto"],
        "meta": meta("Redes Neurais Artificiais, Deep Learning e Algoritmos Genéticos"),
        "output_dir": str(DOCS_DIR / "08-redes-neurais-deep-learning-ag"),
        "filename": "08_RespiraCidadao_Redes_Neurais",
        "sections": [
            {
                "title": "1. ETAPAS 1 A 4: PROBLEMA, DADOS, PREPARO E ARQUITETURA",
                "bullets": [
                    {"text": "Etapa 1, problema: dizer se o ar está bom, carregado ou ruim a partir das 4 medidas do sensor, para avisar escola e UBS antes da crise.", "level": 0},
                    {"text": f"Etapa 2, dados: UCI Air Quality real, {STATS['dataset']['registros_limpos']} horas completas. Nada sintético.", "level": 0},
                    {"text": "Etapa 3, preparo: 70% treino (4.858), 15% validação (1.041) e 15% teste (1.042), com a mesma proporção de níveis. A padronização aprende só com o treino.", "level": 0},
                    {"text": f"Etapa 4, arquitetura: {NN['arquitetura']}. Os dados são 4 números por hora, sem imagem nem sequência longa, então uma rede densa (MLP) basta. CNN e RNN resolveriam problemas que não temos.", "level": 0},
                ],
            },
            {
                "title": "2. ETAPAS 5 A 7: TREINO, REGULARIZAÇÃO E AVALIAÇÃO",
                "tables": [
                    {
                        "headers": ["Experimento", "Épocas", "Treino", "Teste", "F1 médio", "Diferença"],
                        "rows": [
                            [
                                r["modelo"],
                                str(r["epocas"]),
                                pct(r["train_acc"]) if r["train_acc"] is not None else "sem treino",
                                pct(r["test_acc"]),
                                pct(r["test_f1_macro"]),
                                f"{r['gap'] * 100:.1f} pp".replace(".", ",") if r["gap"] is not None else "não se aplica",
                            ]
                            for r in NN["comparacao_experimentos"]
                        ],
                        "col_widths": [64, 18, 24, 24, 24, 26],
                    }
                ],
                "images": [
                    {"path": str(nn_charts / "01_curvas_treinamento.png"), "caption": "Figura 1: Perda e acerto por época, rede sem e com regularização."},
                    {"path": str(nn_charts / "02_matriz_confusao_nn.png"), "caption": "Figura 2: Onde a rede regularizada erra no teste."},
                ],
                "body": [
                    f"A rede A, maior e sem freio, chegou a {pct(nn_base['train_acc'])} no treino e {pct(nn_base['test_acc'])} no teste: {num(nn_base['gap'] * 100, 1)} pontos de diferença, sinal de que decorava. A rede B tem metade dos neurônios, BatchNorm, Dropout de 0,25, weight decay e parada antecipada com paciência de 15 épocas. Parou na época {NN['epocas_executadas']}, voltou ao melhor estado (época {NN['melhor_epoca']}) e ficou com {pct(nn_reg['test_acc'])} no teste e {num(nn_reg['gap'] * 100, 1)} ponto de diferença.",
                    f"Nas {nn_teste} horas de teste, nenhuma hora de ar bom virou ruim e nenhuma ruim virou bom. A regra simples do sensor acerta {pct(nn_regra['test_acc'], 0)}; a rede ganha uns 4 pontos sobre ela.",
                ],
            },
            {
                "title": "3. ETAPA 8: DEMONSTRAÇÃO, LIMITES E DADOS PESSOAIS",
                "tables": [
                    {
                        "headers": ["Leitura nunca vista", "Veredito", "Bom / Carregado / Ruim"],
                        "rows": [
                            [
                                d["cenario"],
                                NIVEL[d["classe_predita"]],
                                " / ".join(pct(d["probabilidades"][k]) for k in ("normal", "atencao", "critico")),
                            ]
                            for d in NN["demonstracao_nao_vista"]
                        ],
                        "col_widths": [70, 30, 80],
                    }
                ],
                "body": [
                    "No produto, os pesos (air_quality_mlp.pt) rodam na central a cada leitura, ao lado da Random Forest. Na tela Como funciona, o card \"Segunda opinião\" mostra o veredito da rede para a leitura que a pessoa montar.",
                    "Limites: base de outra cidade; precisa de recalibração em cada bairro. A rede acerta um pouco menos que a floresta, por isso é segunda opinião e não a voz principal.",
                    "Acessibilidade, segurança, LGPD e sustentabilidade: a rede só recebe 4 números ambientais, nunca dado de pessoa. Treina numa CPU comum e o arquivo de pesos tem 17 KB. O resultado chega ao usuário como cor e palavra, não como probabilidade crua.",
                ],
            },
        ],
    }

    # 09 - Statistical Computing
    it2 = STATS["item_02_normal"]
    it3 = STATS["item_03_testes_hipotese"]
    it4 = STATS["item_04_regressao_simples"]
    it5 = STATS["item_05_regressao_multipla"]
    it6 = STATS["item_06_regressao_logistica"]
    t3a, t3b = it3["teste_3a_unilateral_esquerda"], it3["teste_3b_unilateral_direita"]
    mc = it6["matriz_confusao"]
    corr = it5["matriz_correlacao"]

    doc09 = {
        "title": "RELATÓRIO ESTATÍSTICO DO AR",
        "subtitle": ["O sensor barato consegue dizer quando o ar está ruim?", "Análise da base real UCI Air Quality"],
        "meta": meta("Statistical Computing with R & Python"),
        "output_dir": str(DOCS_DIR / "09-statistical-computing-r-python"),
        "filename": "09_RespiraCidadao_Relatorio_Estatistico",
        "sections": [
            {
                "title": "1. A PERGUNTA E A BASE (ITEM 01)",
                "body": [
                    "Cliente: secretaria municipal que quer instalar sensores de baixo custo em escolas e UBS. Pergunta: as medidas de um sensor barato explicam o monóxido de carbono que uma estação oficial mediria? Se sim, dá para avisar escolas sem pagar por uma estação em cada bairro (ODS 3 e 11).",
                    f"Base: {STATS['dataset']['nome']}, dados públicos do repositório da UC Irvine. São {STATS['dataset']['registros_brutos']} horas em que um sensor de baixo custo e um analisador de referência mediram o mesmo ar urbano. Tiramos as horas com falha (-200) e ficamos com {STATS['dataset']['registros_limpos']}. Escolhemos essa base porque ela tem exatamente o par que nos interessa: sensor barato ao lado de medida oficial.",
                    f"Níveis pelo CO(GT): {STATS['dataset']['distribuicao_risco']['normal']} horas bom (abaixo de 1,5 mg/m³), {STATS['dataset']['distribuicao_risco']['atencao']} carregado (1,5 a 3,0) e {STATS['dataset']['distribuicao_risco']['critico']} ruim (3,0 ou mais).",
                ],
            },
            {
                "title": "2. DISTRIBUIÇÃO NORMAL E TESTES DE HIPÓTESE (ITENS 02 E 03)",
                "tables": [
                    {
                        "headers": ["Item", "Pergunta", "Resultado", "Decisão"],
                        "rows": [
                            ["02a", "P(X < média) de CO(GT)", f"{pct(it2['p_menor_media'], 2)} (média {num(it2['media'], 4)} mg/m³)", it2["classificacao_a"]],
                            ["02b", "P(X > mediana) de CO(GT)", f"{pct(it2['p_maior_mediana'], 2)} (mediana {num(it2['mediana'], 1)} mg/m³)", it2["classificacao_b"]],
                            ["03a", "H1: média < média da base (n=20, alfa=6%)", f"média da amostra {num(t3a['media_amostral'])}; Z={num(t3a['z_calculado'], 4)}; Z crítico {num(t3a['z_critico'], 4)}; p={num(t3a['p_valor'], 4)}", t3a["decisao"]],
                            ["03b", "H1: média > média da base (n=25, alfa=9%)", f"média da amostra {num(t3b['media_amostral'])}; Z={num(t3b['z_calculado'], 4)}; Z crítico {num(t3b['z_critico'], 4)}; p={num(t3b['p_valor'], 4)}", t3b["decisao"]],
                        ],
                        "col_widths": [14, 52, 70, 44],
                    }
                ],
                "body": [
                    "A média (2,18) fica acima da mediana (1,9): a cauda direita é longa, com poucas horas de monóxido muito alto. Por isso P(X > mediana) sob a Normal dá 57,8%, e não 50%. Essas horas raras da cauda são justamente as que o produto precisa pegar.",
                    "Nos dois testes as amostras sorteadas não mostram diferença da média da base. É o esperado para amostras aleatórias da mesma população, e confirma que amostras pequenas não servem para tirar conclusão sobre um bairro.",
                ],
                "images": [{"path": str(stats_charts / "02_distribuicao_normal_co.png"), "caption": "Figura 1: Distribuição de CO(GT) e a curva Normal com a mesma média e desvio."}],
            },
            {
                "title": "3. UM SENSOR SÓ: REGRESSÃO SIMPLES (ITEM 04)",
                "body": [
                    f"a) A dispersão entre o sensor de monóxido PT08.S1(CO) e o CO(GT) da estação forma uma nuvem estreita que sobe para a direita. Quando o sensor sobe, o monóxido real sobe junto.",
                    f"b) Covariância {num(it4['covariancia'], 2)} e correlação de Pearson r = {num(it4['pearson_r'], 3)}, com p < 0,0001. Relação positiva e forte.",
                    "c) O gráfico por decis mostra a média de CO(GT) subindo de forma quase reta a cada faixa do sensor.",
                    f"d) Equação: {it4['equacao'].replace('.', ',')}.",
                    f"e) R² = {pct(it4['r2'], 2)} e teste F = {num(it4['teste_f'], 2)} (p < 0,0001). Só o sensor de monóxido já explica três quartos da variação do monóxido real.",
                    f"f) Previsão: com o sensor em 1350, o CO previsto é {num(it4['previsao_exemplo']['co_previsto'], 3)} mg/m³, nível ruim.",
                ],
                "images": [
                    {"path": str(stats_charts / "04_dispersao_regressao_simples.png"), "caption": "Figura 2: Dispersão com a reta ajustada e o ponto previsto."},
                    {"path": str(stats_charts / "04_correlacao_bivariada.png"), "caption": "Figura 3: Correlação por decis do sensor."},
                ],
            },
            {
                "title": "4. AS QUATRO MEDIDAS DO SENSOR: REGRESSÃO MÚLTIPLA (ITEM 05)",
                "body": [
                    "Usamos as quatro medidas que nosso ESP32 tem: os dois sensores de gás PT08.S1(CO) e PT08.S2(NMHC), temperatura (T) e umidade (RH).",
                    f"a) e b) Os dois sensores de gás andam com o CO(GT) (r = {num(corr['CO(GT)']['PT08.S1(CO)'], 3)} e {num(corr['CO(GT)']['PT08.S2(NMHC)'], 3)}) e entre si (r = {num(corr['PT08.S1(CO)']['PT08.S2(NMHC)'], 3)}), então carregam informação parecida. Temperatura e umidade quase não se relacionam com o CO sozinhas (r = {num(corr['CO(GT)']['T'], 3)} e {num(corr['CO(GT)']['RH'], 3)}), mas se relacionam entre si (r = {num(corr['T']['RH'], 3)}) e corrigem a leitura dos sensores de gás, que mudam com o clima.",
                    f"d) Equação: {it5['equacao'].replace('.', ',')}.",
                    f"e) R² = {pct(it5['r2'], 2)} (ajustado {pct(it5['r2_ajustado'], 2)}) e teste F = {num(it5['teste_f'], 2)} (p < 0,0001). As quatro medidas juntas explicam 88% da variação, contra 77% de um sensor só.",
                    f"f) Previsões: {it5['previsoes'][0]['cenario']} = {num(it5['previsoes'][0]['co_previsto'], 3)} mg/m³ (carregado); {it5['previsoes'][1]['cenario']} = {num(it5['previsoes'][1]['co_previsto'], 3)} mg/m³ (ruim).",
                ],
                "tables": [
                    {
                        "headers": ["Covariância", "CO(GT)", "PT08.S1(CO)", "PT08.S2(NMHC)", "T", "RH"],
                        "rows": [
                            [nome] + [num(it5["matriz_covariancia"][nome][col], 2) for col in it5["matriz_covariancia"]]
                            for nome in it5["matriz_covariancia"]
                        ],
                        "col_widths": [34, 26, 32, 34, 26, 28],
                    }
                ],
                "images": [
                    {"path": str(stats_charts / "05_dispersao_multivariada.png"), "caption": "Figura 4: Cada medida do sensor contra o CO(GT)."},
                    {"path": str(stats_charts / "05_matriz_correlacao.png"), "caption": "Figura 5: Matriz de correlação de Pearson."},
                ],
            },
            {
                "title": "5. AR RUIM OU NÃO: REGRESSÃO LOGÍSTICA (ITEM 06)",
                "body": [
                    f"a) Evento: ar ruim (CO(GT) de 3,0 mg/m³ ou mais). Equação: {it6['equacao_logit'].replace('.', ',')}.",
                    f"b) No teste, com {sum(sum(l) for l in mc)} horas: {mc[0][0]} horas boas reconhecidas, {mc[1][1]} horas ruins reconhecidas, {mc[0][1]} alarmes falsos e {mc[1][0]} horas ruins perdidas. Acurácia {pct(it6['acuracia_teste'], 2)}, precisão {pct(it6['precision_critico'], 2)}, recall {pct(it6['recall_critico'], 2)}. De cada 100 horas de ar ruim, o modelo pega 86. As 14 que escapam são o motivo de o sensor também ter a regra local de luz.",
                    f"c) Classificação: {it6['classificacoes_exemplo'][0]['cenario']} deu P(ruim) = {pct(it6['classificacoes_exemplo'][0]['prob_critico'], 2)}, classe 0. {it6['classificacoes_exemplo'][1]['cenario']} deu P(ruim) = {pct(it6['classificacoes_exemplo'][1]['prob_critico'], 2)}, classe 1.",
                ],
                "images": [{"path": str(stats_charts / "06_matriz_confusao_logistica.png"), "caption": "Figura 6: Matriz de confusão da regressão logística."}],
            },
            {
                "title": "6. O QUE RECOMENDAMOS (ITEM 07)",
                "bullets": [
                    {"text": f"Sim, o sensor barato serve. As quatro medidas explicam {pct(it5['r2'], 0)} do monóxido real e acertam {pct(it6['acuracia_teste'], 0)} das horas na decisão ar ruim ou não.", "level": 0},
                    {"text": "Instale com as quatro medidas, não só com o sensor de gás. Temperatura e umidade sozinhas não dizem nada, mas somadas aos gases sobem o R² de 77% para 88%.", "level": 0},
                    {"text": "Mantenha a luz local no sensor. O modelo perde 14 de cada 100 horas ruins; a regra no aparelho cobre quando a rede cai ou o modelo erra.", "level": 0},
                    {"text": "Recalibre em cada bairro. A base é de outra cidade, e os testes de hipótese mostram que poucas horas de amostra não bastam para concluir nada sobre um lugar novo.", "level": 0},
                ],
            },
        ],
    }

    for doc in [doc01, doc02, doc03, doc05, doc06, doc07, doc08, doc09]:
        render_doc(doc)
        print(f"[OK] Gerado DOCX + PDF: {doc['output_dir']}/{doc['filename']}.pdf")


if __name__ == "__main__":
    build_all()
