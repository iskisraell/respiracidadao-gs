#!/usr/bin/env python3
"""
Gera os documentos de entrega (DOCX + PDF) com o gerador fiap-doc, a partir dos números reais
dos artefatos, em linguagem direta, sem jargão solto entre parênteses e sem travessões.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
JSON_DIR = DOCS_DIR / "json_sources"
JSON_DIR.mkdir(parents=True, exist_ok=True)

_FIAP_GEN_CANDIDATES = [
    Path(os.environ["FIAP_DOC_GENERATOR"]) if os.environ.get("FIAP_DOC_GENERATOR") else None,
    Path.home() / ".agents" / "skills" / "fiap-doc" / "scripts" / "generate.py",
    Path.home() / "projects" / "fleet" / "skills" / "fiap-doc" / "scripts" / "generate.py",
]
FIAP_GEN = next((c for c in _FIAP_GEN_CANDIDATES if c and c.exists()), None)
if FIAP_GEN is None:
    sys.exit("Gerador fiap-doc não encontrado. Defina FIAP_DOC_GENERATOR com o caminho de generate.py.")
_VENV_CANDIDATE = ROOT / ".venv" / "bin" / "python"
VENV_PY = str(_VENV_CANDIDATE if _VENV_CANDIDATE.exists() else Path(sys.executable))

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


def ent(e: dict) -> str:
    return f"{e['PT08.S1(CO)']:.0f}, {e['PT08.S2(NMHC)']:.0f}, {e['T']:.0f} °C e {e['RH']:.0f}% de umidade"


def conf(p: float) -> str:
    return "acima de 99%" if p >= 0.995 else pct(p, 0)


def dec(texto):
    return re.sub(r"(?<=\d)\.(?=\d)", ",", texto)


def mil(n):
    return f"{int(n):,}".replace(",", ".")


FI_NOME = {"PT08.S2(NMHC)": "fumaça e gases", "T": "temperatura", "PT08.S1(CO)": "monóxido de carbono", "RH": "umidade"}


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
    evid = DOCS_DIR / "evidencias"
    uml_seq = str(assets / "uml_sequencia_leitura.png")

    regra, campo, lab = ML["comparacao_conjuntos"]
    nn_regra, nn_base, nn_reg = NN["comparacao_experimentos"]
    ml_teste = sum(sum(l) for l in ML["matriz_confusao"])
    nn_teste = sum(sum(l) for l in NN["matriz_confusao"])

    # 01 - AI Challenges
    doc01 = {
        "title": "RESPIRACIDADÃO",
        "subtitle": ["O ar perto de você, em uma frase", "Visão geral do projeto integrador"],
        "subtitle_note": "Problema, arquitetura, demonstração e próximos passos",
        "meta": meta("AI Challenges"),
        "output_dir": str(DOCS_DIR / "01-ai-challenges"),
        "filename": "01_RespiraCidadao_Dossie_Integrador",
        "sections": [
            {
                "title": "1. O PROBLEMA E PARA QUEM",
                "body": [
                    "Uma diretora abre o celular às 7h40 e lê: \"Ar ruim perto da escola agora. Mantenha as janelas fechadas e deixe a educação física para depois do almoço.\" O RespiraCidadão existe para que essa frase chegue a tempo e seja confiável.",
                    "A Organização Mundial da Saúde estima cerca de 7 milhões de mortes por ano ligadas à poluição do ar. Fumaça de queimada e trânsito pesado disparam crises de asma e bronquite crônica. Quem sente primeiro são crianças, idosos e pacientes de postos de saúde na periferia, onde quase não há estação oficial de medição. Quando o boletim da cidade sai, ele fala da região inteira e chega tarde.",
                    "O produto atende três perfis: a coordenação de escola ou posto de saúde, que decide se a atividade fica ao ar livre; a família com criança, idoso ou alguém com asma, que precisa saber se é seguro sair; e o vizinho que viu fumaça e quer avisar o bairro.",
                ],
                "bullets": [
                    {"text": "ODS 3, saúde e bem-estar: avisar antes da crise respiratória.", "level": 0},
                    {"text": "ODS 10, redução das desigualdades: levar medição de baixo custo a bairros sem estação oficial.", "level": 0},
                    {"text": "ODS 11, cidades sustentáveis: gerar dados ambientais abertos e verificáveis por bairro.", "level": 0},
                    {"text": "Da discussão sobre tecnologia cidadã na live de lançamento, adotamos uma regra clara: o morador não precisa aprender termos técnicos para usar o sistema. A tela principal fala só de ar, lugar, horário e ação.", "level": 0},
                ],
            },
            {
                "title": "2. COMO A INFORMAÇÃO CHEGA ATÉ A PESSOA",
                "body": [
                    "Um sensor pequeno na parede da escola mede quatro coisas: fumaça e gases, monóxido de carbono, temperatura e umidade. Quando o ar piora, a luz muda de cor e o alarme toca na hora, mesmo se a internet cair.",
                    "Em paralelo, a leitura vai para a central, que confere o resultado usando um modelo treinado em 6.941 horas de medições reais e devolve o nível de risco com a porcentagem de confiança. O aplicativo traduz isso em cor, uma frase simples e o que fazer agora.",
                ],
                "images": [
                    {"path": arch_png, "caption": "Figura 1: Componentes do RespiraCidadão e o caminho de cada leitura.", "width": 165},
                    {"path": uml_seq, "caption": "Figura 2: Diagrama de sequência de uma leitura de ar ruim, usado pelo grupo para padronizar a mensagem entre sensor, central e aplicativo.", "width": 165},
                ],
                "tables": [
                    {
                        "headers": ["Parte do sistema", "Papel no produto", "Disciplina responsável"],
                        "rows": [
                            ["Sensor no local", "Mede gases, temperatura e umidade, acende a luz certa e envia a leitura", "AI Computer Systems & Sensors"],
                            ["Base e validação estatística", "Prova que as 4 medidas do sensor explicam 88% do monóxido de laboratório e define os limiares", "Statistical Computing"],
                            ["Central local", "Recebe e valida cada leitura, guarda o histórico em planilha e banco e alimenta o aplicativo", "Computational Thinking with Python"],
                            ["Central na nuvem", "Roda a mesma ingestão sob demanda na AWS, gravando em banco PostgreSQL gerenciado e registrando eventos", "Cloud Computing & Serverless"],
                            ["Modelo principal", f"Acerta {round(campo['accuracy'] * 100)} de cada 100 horas usando apenas as 4 medidas do sensor", "Machine Learning & Modelling"],
                            ["Segunda opinião", f"Rede neural independente que confere o veredito, acertando {pct(NN['teste_accuracy'], 0)} no teste", "Redes Neurais e Deep Learning"],
                            ["Segurança e privacidade", "Trava enxurradas de envios, exige chave para apagar dados, limpa relatos e assina cada leitura", "Cognitive Cybersecurity"],
                        ],
                        "col_widths": [38, 86, 56],
                    }
                ],
            },
            {
                "title": "3. DEMONSTRAÇÃO",
                "body": [
                    "O aplicativo tem duas telas. A tela Agora mostra cada lugar com sua cor, o que fazer, o melhor horário para atividade ao ar livre e os relatos dos vizinhos. A tela Como funciona explica o caminho da informação, deixa testar uma leitura ao vivo e deixa claro o que ainda falta para ir para a rua.",
                ],
                "images": [
                    {"path": str(assets / "app_agora.png"), "caption": "Figura 3: Tela Agora com a escola em ar ruim e a central concordando com 93% de confiança.", "width": 160},
                    {"path": str(assets / "app_horario_relatos.png"), "caption": "Figura 4: Melhor horário calculado da base real e relato de vizinho marcado como urgente.", "width": 160},
                    {"path": str(wokwi / "wokwi_3_ar_ruim.png"), "caption": "Figura 5: Sensor simulado no Wokwi com o LED vermelho aceso.", "width": 160},
                ],
            },
            {
                "title": "4. O QUE FUNCIONA HOJE, DECISÕES E PRÓXIMOS PASSOS",
                "tables": [
                    {
                        "headers": ["Parte", "Funciona hoje", "Próximo passo"],
                        "rows": [
                            ["Sensor", "Circuito completo no simulador Wokwi, alerta local por luz e som e envio estruturado", "Montar a placa física com bateria solar e rádio para áreas sem Wi-Fi"],
                            ["Central local", "API em Python com modelos integrados, histórico, relatos, padrão por hora e 24 testes automáticos", "Conectar o aplicativo diretamente ao endereço público na nuvem"],
                            ["Central na nuvem", "Publicada e validada na AWS com função sob demanda, monitoramento e banco PostgreSQL cifrado", "Colocar banco e função em rede privada corporativa e ativar cota paga de IA externa"],
                            ["Modelos de IA", "Treinados em base real e avaliados em meses que nunca viram", "Recalibrar por algumas semanas ao lado de uma estação oficial da CETESB"],
                            ["Aviso ao morador", "Aplicativo web para celular e computador", "Enviar alerta no WhatsApp quando o local favorito entrar em nível ruim"],
                        ],
                        "col_widths": [30, 80, 70],
                    }
                ],
                "body": [
                    "Organizamos o time em três frentes presas ao mesmo formato de mensagem: uma cuidou do sensor e da nuvem, outra da estatística e dos modelos de inteligência artificial, e a terceira da central em Python, do aplicativo e das proteções de segurança. Cada etapa só fechava quando os testes automáticos passavam.",
                    "Duas dificuldades mudaram o projeto para melhor. Primeiro, o modelo com 11 medidas de laboratório acertava um pouco mais, mas nenhuma escola teria aquele equipamento. Cortamos para as 4 medidas do sensor barato e aceitamos perder um ponto de acerto. Segundo, a versão gratuita do simulador de circuito não acessa servidores externos. Em vez de contornar isso com um atalho artificial, fizemos o sensor tratar a falta de rede como cenário real, mantendo a luz e o alarme locais ativos, e validamos o envio em rede tanto no servidor Python local quanto na AWS real.",
                ],
            },
            {
                "title": "5. ACESSIBILIDADE, SEGURANÇA, PRIVACIDADE E SUSTENTABILIDADE",
                "bullets": [
                    {"text": "Acessibilidade: todo alerta combina cor, palavra clara como Bom, Carregado ou Ruim e alarme sonoro no sensor para quem não olha a tela ou tem daltonismo.", "level": 0},
                    {"text": "Segurança: limite de 30 envios por minuto por endereço, chave obrigatória para apagar dados, limpeza de código malicioso nos relatos, assinatura digital em cada leitura e criptografia na nuvem.", "level": 0},
                    {"text": "Privacidade e LGPD: o relato de vizinho não pede nome, telefone nem localização da pessoa. Guardamos apenas o texto e o local escolhido.", "level": 0},
                    {"text": "Sustentabilidade: modelos leves que rodam em computador comum, sensor de baixo consumo e nuvem sob demanda que só executa quando chega uma leitura.", "level": 0},
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
                "title": "1. O PROBLEMA E POR QUE UM SENSOR NO LOCAL",
                "body": [
                    "Escolas e postos de saúde da periferia ficam longe das estações oficiais de qualidade do ar. Quando a fumaça chega, ninguém no prédio percebe até alguém começar a tossir. Um sensor pequeno na parede resolve a parte mais urgente: avisa quem está ali na hora, com luz e som, e envia a medição para a central do bairro.",
                    "A Organização Mundial da Saúde estima cerca de 7 milhões de mortes por ano ligadas à poluição do ar, e crianças respiram mais ar por quilo de corpo que adultos. O projeto se conecta diretamente ao ODS 3, de saúde e bem-estar, e ao ODS 11, de cidades sustentáveis.",
                ],
            },
            {
                "title": "2. O CIRCUITO E COMO ELE DECIDE",
                "tables": [
                    {
                        "headers": ["Componente", "Pino no ESP32", "Função no circuito"],
                        "rows": [
                            ["Sensor de fumaça e gases", "GPIO 34", "Medida principal que define a cor da luz. Simulado por potenciômetro no Wokwi."],
                            ["Sensor de monóxido de carbono", "GPIO 35", "Segunda medida de gás, enviada para a central conferir. Também simulado por potenciômetro."],
                            ["Sensor DHT22", "GPIO 15", "Mede temperatura e umidade. Ar quente e seco prende a fumaça perto do chão."],
                            ["LEDs verde, amarelo e vermelho", "GPIO 26, 27 e 14", "Mostram o estado do ar para quem passa, ligados com resistores de 220 ohms."],
                            ["Buzzer", "GPIO 25", "Emite bip curto em ar carregado e alarme longo em ar ruim para quem não está olhando."],
                        ],
                        "col_widths": [56, 32, 92],
                    }
                ],
                "body": [
                    "O código embarcado no ESP32 classifica cada gás com regras simples que funcionam sem internet. Para fumaça e gases, valores abaixo de 830 indicam ar bom, de 830 a 1139 indicam ar carregado e 1140 ou mais indicam ar ruim. Para monóxido de carbono, os cortes ficam em 1010 e 1280. Esses números seguem a mesma escala dos sensores de óxido metálico da base real usada pelo grupo, que vai de 380 a 2250.",
                    "Quando a umidade cai abaixo de 30%, o monitor serial sinaliza ar seco e envia o dado para a central, sem alterar a cor da luz. Testamos essa regra local em 1.389 horas reais separadas para avaliação: sozinha, sem depender de internet, ela acerta 84 de cada 100 horas.",
                    "A cada 3 segundos o ESP32 monta uma mensagem em formato JSON com o identificador do sensor, localização do prédio e as quatro medições, e tenta enviá-la por HTTP para a central. É exatamente o mesmo formato aceito pela API em Python e pela função na nuvem.",
                ],
            },
            {
                "title": "3. OS TRÊS COMPORTAMENTOS DEMONSTRADOS",
                "tables": [
                    {
                        "headers": ["Situação", "Leitura do sensor", "Resposta no aparelho", "Resposta da central"],
                        "rows": [
                            ["Ar bom na UBS de manhã", "Gases 706, CO 925, 18 °C, 55% umidade", "LED verde e buzzer mudo", "Aceito, Bom, 100% de confiança"],
                            ["Ar carregado na praça", "Gases 980, CO 1120, 24 °C, 42% umidade", "LED amarelo e bip curto", "Aceito, Carregado, 95% de confiança"],
                            ["Ar ruim perto da escola", "Gases 1280, CO 1383, 31 °C, 34% umidade", "LED vermelho e alarme contínuo", "Aceito, Ruim, 93% de confiança"],
                        ],
                        "col_widths": [40, 56, 42, 42],
                    }
                ],
                "body": [
                    "Esses três cenários foram reproduzidos tanto no simulador Wokwi, girando os potenciômetros à mão, quanto pelo script run_3_cenarios.py enviando os mesmos dados para a central. Nos prints do simulador, o ajuste manual parou a uma unidade desses valores e acionou exatamente as mesmas luzes e alarmes.",
                ],
            },
            {
                "title": "4. PRINTS DO SIMULADOR",
                "images": [
                    {"path": str(wokwi / "wokwi_1_ar_bom.png"), "caption": "Figura 1: Ar bom. LED verde aceso e mensagem JSON exibida no monitor serial.", "width": 150},
                    {"path": str(wokwi / "wokwi_2_ar_carregado.png"), "caption": "Figura 2: Ar carregado. LED amarelo aceso.", "width": 150},
                    {"path": str(wokwi / "wokwi_3_ar_ruim.png"), "caption": "Figura 3: Ar ruim. LED vermelho aceso e alarme disparado.", "width": 150},
                ],
            },
            {
                "title": "5. A LEITURA CHEGANDO E VIRANDO PLANILHA CSV",
                "body": [
                    "A versão gratuita do simulador Wokwi não alcança servidores fora do navegador. Para comprovar a recepção e a gravação dos dados, usamos o receptor Python receiver_csv.py recebendo o mesmo JSON dos três cenários e salvando cada leitura com data e hora no arquivo CSV.",
                ],
                "images": [{"path": str(evid / "02_json_csv.png"), "caption": "Figura 4: Receptor Python confirmando as três leituras e gravando as linhas no CSV.", "width": 165}],
            },
            {
                "title": "6. O QUE É REAL E O QUE É SIMULADO",
                "bullets": [
                    {"text": "Real: código do ESP32 em C++, esquema do circuito em diagram.json, receptor Python que grava CSV e o script que reproduz os três cenários contra a central.", "level": 0},
                    {"text": "Simulado: os dois sensores de gás são representados por potenciômetros no simulador. Num aparelho físico, sensores de gás precisam de aquecimento e calibração ao lado de uma estação oficial antes de valerem como medida.", "level": 0},
                    {"text": "Comportamento sem internet: quando a rede falha ou o simulador bloqueia o acesso externo, o sensor registra que está sem rede e mantém a luz e o alarme local funcionando. Esse é justamente o comportamento esperado numa escola durante uma queda de Wi-Fi.", "level": 0},
                ],
            },
        ],
    }

    # 03 - Cognitive Cybersecurity
    doc03 = {
        "title": "RESPIRACIDADÃO: SEGURANÇA E PRIVACIDADE",
        "subtitle": ["Onde o sistema pode ser atacado e como se defende", "Consultoria de cibersegurança e adequação à LGPD"],
        "meta": meta("Cognitive Cybersecurity"),
        "output_dir": str(DOCS_DIR / "03-cognitive-cybersecurity"),
        "filename": "03_RespiraCidadao_Cybersecurity",
        "sections": [
            {
                "title": "1. A SOLUÇÃO E POR QUE A SEGURANÇA IMPORTA",
                "body": [
                    "O RespiraCidadão avisa escolas, postos de saúde e famílias quando a qualidade do ar piora no bairro. O público principal reúne crianças, idosos e pessoas com asma na periferia.",
                    "A arquitetura passa por quatro pontos: o usuário no aplicativo e o sensor ESP32 na ponta, a aplicação web com a central em Python no meio, o banco de dados guardando o histórico e os modelos de inteligência artificial classificando o risco. O sensor entra pela mesma porta da central que o aplicativo, passando pelas mesmas validações e pelo mesmo limite de envios.",
                    "Nesse produto, segurança afeta decisões reais. Um alarme falso faz uma escola cancelar aulas sem motivo. Um alarme bloqueado ou adulterado deixa crianças respirando fumaça. As proteções impedem enxurradas de alertas falsos, apagamento sem permissão e alteração silenciosa do histórico.",
                ],
            },
            {
                "title": "2. SUPERFÍCIE DE ATAQUE EM CINCO CAMADAS",
                "tables": [
                    {
                        "headers": ["Camada", "Ameaça provável", "Consequência se acontecer"],
                        "rows": [
                            ["Usuários", "Mensagem falsa pedindo a chave de administração ou envio em massa de relatos falsos", "Alguém apaga o histórico ou provoca pânico sem haver queimada"],
                            ["Aplicação", "Código malicioso escondido no texto de um relato ou fórmula inserida para atacar quem abrir o CSV", "Execução de código no navegador de quem lê ou na planilha da secretaria"],
                            ["API", "Enxurrada de requisições automáticas e tentativa de falsificar o endereço IP para burlar o limite", "Central fora do ar justamente durante uma queimada real"],
                            ["Banco de dados", "Alteração direta no arquivo salvo ou ataque de injeção de comandos SQL", "Histórico ambiental adulterado sem deixar rastros"],
                            ["Modelo de IA", "Envio de leituras absurdas fora da realidade para confundir a classificação", "Sistema indica ar bom enquanto há fumaça no bairro"],
                        ],
                        "col_widths": [28, 78, 74],
                    }
                ],
            },
            {
                "title": "3. MATRIZ DE RISCOS",
                "tables": [
                    {
                        "headers": ["Risco", "Probabilidade e impacto", "Controle adotado"],
                        "rows": [
                            ["Enxurrada de envios na API", "Alta probabilidade, impacto alto", "Limite de 30 envios por minuto por endereço, bloqueando excessos com resposta de limite excedido"],
                            ["Apagar histórico sem permissão", "Média probabilidade, impacto crítico", "Exigência de chave administrativa comparada de forma segura; se nenhuma chave estiver configurada no servidor, a rota fica fechada"],
                            ["Código malicioso ou fórmula em relato", "Alta probabilidade, impacto médio", "Qualquer marcação HTML é removida antes de gravar, e textos que começam com sinais de fórmula ganham proteção antes de ir para o CSV"],
                            ["Adulteração do histórico no banco", "Baixa probabilidade, impacto alto", "Assinatura digital HMAC gerada com chave guardada fora do banco, cobrindo todos os campos da leitura e verificável a qualquer momento"],
                            ["Leitura falsa para enganar a IA", "Média probabilidade, impacto alto", "Cada medida passa por faixas numéricas válidas antes de chegar ao modelo; valores impossíveis são recusados na entrada"],
                            ["Engenharia social com a equipe", "Alta probabilidade, impacto alto", "Uso de um único endereço oficial em HTTPS, orientação da equipe para nunca passar chaves por mensagem e autenticação em duas etapas para gestores"],
                        ],
                        "col_widths": [48, 36, 96],
                    }
                ],
            },
            {
                "title": "4. CONTROLES APLICADOS E JUSTIFICATIVA",
                "body": [
                    "Priorizamos controles simples de manter, baratos e provados em código e na nuvem. Como os dados ambientais são públicos e o morador não precisa criar conta, não faz sentido colocar senha para consultar o ar do bairro. A proteção se concentra em quem escreve, em quem apaga, na integridade do histórico e no tráfego até o banco na nuvem.",
                ],
                "tables": [
                    {
                        "headers": ["Categoria", "O que fizemos", "Situação atual"],
                        "rows": [
                            ["Autenticação", "Chave secreta para rotas administrativas na central local e credenciais do banco isoladas em variáveis de ambiente na AWS, sem nenhuma senha no código. Autenticação em duas etapas planejada para gestores.", "Implementado; duas etapas planejado"],
                            ["Firewall e limite de tráfego", "Limite de envios por endereço IP na central e regra de firewall na AWS liberando apenas a porta do banco PostgreSQL. O recurso CORS do navegador ajuda contra outros sites, mas não bloqueia robôs diretos, por isso o limite fica no servidor.", "Implementado; filtro web dedicado planejado"],
                            ["Backup", "Retenção automática de cópias gerenciada pelo banco PostgreSQL na AWS e histórico paralelo em planilha com assinatura digital em cada linha.", "Ativo na AWS; rotina externa planejada"],
                            ["Criptografia", "Conexão protegida por HTTPS na URL pública da AWS, criptografia obrigatória no caminho até o banco e disco do banco cifrado em repouso na nuvem. No protótipo local em computador pessoal, os arquivos ficam sem cifra.", "Validado na AWS"],
                            ["Monitoramento", "Trilha de eventos de segurança protegida por chave na central local e registros automáticos de alerta no CloudWatch da AWS para leituras inválidas ou críticas.", "Implementado; alertas por mensagem planejados"],
                            ["Proteção dos modelos de IA", "Validação de faixas antes de chamar os modelos e carregamento seguro dos pesos da rede neural, impedindo execução de código escondido no arquivo. Próximo passo: conferir a assinatura dos arquivos de modelo ao iniciar.", "Parcialmente implementado"],
                        ],
                        "col_widths": [30, 106, 44],
                    }
                ],
            },
            {
                "title": "5. PROTEÇÕES FUNCIONANDO NA PRÁTICA",
                "body": [
                    "Não ficamos apenas na proposta. Cada proteção da central em Python tem teste automatizado rodando e passando, num total de 24 testes, além de testes manuais simulando ataques reais no terminal. Na AWS, validamos diretamente a criptografia em trânsito, o disco cifrado do banco, o isolamento de credenciais em variáveis de ambiente e o descarte de leituras inválidas nos logs.",
                ],
                "bullets": [
                    {"text": "Bloqueio de enxurrada: ao ultrapassar o limite configurado, a central passa a recusar os envios seguintes e registra o bloqueio na auditoria.", "level": 0},
                    {"text": "Resistência a IP falsificado: tentar enganar o limite mudando o cabeçalho de origem não funciona, porque a central ignora esse cabeçalho fora de um proxy confiável.", "level": 0},
                    {"text": "Proteção contra apagamento: tentar limpar o histórico sem chave ou com chave errada é recusado na hora.", "level": 0},
                    {"text": "Limpeza de texto e planilhas: código escondido em um relato é removido antes de gravar, e comandos de planilha deixam de ser executáveis no CSV.", "level": 0},
                    {"text": "Detecção de adulteração: alteramos manualmente uma leitura direto no banco de dados e a rota de verificação acusou imediatamente que a assinatura digital não batia mais.", "level": 0},
                ],
            },
            {
                "title": "6. EVIDÊNCIAS NO TERMINAL E NA AWS",
                "images": [
                    {"path": str(evid / "03_limite_chave.png"), "caption": "Figura 1: Bloqueio automático após excesso de envios e recusa de apagamento sem chave válida.", "width": 158},
                    {"path": str(evid / "03_selo.png"), "caption": "Figura 2: Assinatura válida antes da edição, alerta de adulteração após mexer direto no banco e recuperação após desfazer a alteração.", "width": 158},
                    {"path": str(evid / "03_pytest.png"), "caption": "Figura 3: Os 24 testes automáticos de segurança e funcionamento passando.", "width": 158},
                    {"path": str(evid / "07_aws_rds_console.png"), "caption": "Figura 4: Banco PostgreSQL ativo na AWS com disco cifrado e acesso restrito por firewall.", "width": 158},
                ],
            },
            {
                "title": "7. PRIVACIDADE, LGPD E ENGENHARIA SOCIAL",
                "tables": [
                    {
                        "headers": ["Pergunta", "Resposta do projeto"],
                        "rows": [
                            ["Quais dados pessoais são tratados?", "Apenas o endereço IP de quem envia dados, que a LGPD considera dado pessoal. Ele fica restrito ao registro de segurança para impedir abusos e investigar ataques, apoiado na base legal de legítimo interesse. Fora isso, não existe cadastro: o sensor envia só o código do aparelho e a coordenada pública do prédio, e o relato leva só o texto e o bairro."],
                            ["Quem pode ver o registro de segurança?", "Somente quem possui a chave administrativa. Para operação contínua, planejamos apagar esses registros automaticamente após 30 dias."],
                            ["Pode haver dado sensível?", "Sim. Um morador pode escrever algo sobre saúde, como falta de ar de uma criança. Justamente por isso não pedimos nome, telefone nem endereço pessoal."],
                            ["Como protegemos esses dados?", "Coleta mínima, limpeza do texto, chave para apagar, criptografia em trânsito e no banco da nuvem e assinatura digital em cada registro."],
                            ["Como o usuário é informado?", "O próprio formulário de relato avisa de forma direta: \"Sem nome, sem localização sua. Só o texto.\" A tela Como funciona detalha essas regras."],
                        ],
                        "col_widths": [48, 132],
                    }
                ],
                "body": [
                    "Cenário de engenharia social: a diretora de uma escola recebe no WhatsApp uma mensagem fingindo ser da Defesa Civil, pedindo para instalar um aplicativo falso de alerta ou enviar a chave de acesso do painel. Contramedidas: o RespiraCidadão só funciona num único endereço oficial em HTTPS divulgado pela secretaria, a equipe recebe orientação clara de que ninguém pede chave por mensagem e as contas administrativas usam autenticação em duas etapas.",
                ],
            },
        ],
    }

    # 05 - Computational Thinking with Python
    doc05 = {
        "title": "RESPIRACIDADÃO: A CENTRAL EM PYTHON",
        "subtitle": ["API que recebe o sensor, decide o nível e guarda o histórico", "Servidor FastAPI com gravação em CSV e indicadores"],
        "meta": meta("Computational Thinking with Python"),
        "output_dir": str(DOCS_DIR / "05-computational-thinking-with-python"),
        "filename": "05_RespiraCidadao_API_Python",
        "sections": [
            {
                "title": "1. O QUE A CENTRAL FAZ",
                "body": [
                    "O sensor na parede da escola só sabe acender uma luz e tocar um alarme. Quem guarda o histórico, confere a leitura com o modelo de inteligência artificial e responde ao aplicativo é a central em Python. Ela recebe os dados do ESP32, recusa leituras incompletas ou absurdas, decide o nível do ar com uma função condicional, grava a linha com data e hora no arquivo CSV e no banco local e recalcula os indicadores a cada consulta.",
                    "Os dois sensores de gás devolvem índices numéricos que sobem conforme o ar piora. Os limiares ficam guardados em um dicionário Python: para fumaça e gases, atenção em 830 e crítico em 1140; para monóxido de carbono, atenção em 1010 e crítico em 1280. São exatamente os mesmos cortes do sensor e da versão na nuvem.",
                ],
                "images": [{"path": uml_seq, "caption": "Figura 1: Fluxo de uma leitura, do sensor até o aplicativo.", "width": 165}],
            },
            {
                "title": "2. ROTAS DA API",
                "tables": [
                    {
                        "headers": ["Rota", "Método", "Função"],
                        "rows": [
                            ["/ocorrencias", "POST", "Valida cada campo, recusa leitura inválida com erro 400, classifica o risco, grava em CSV e banco local e devolve 201"],
                            ["/ocorrencias", "GET", "Lista as leituras salvas, permitindo filtrar por nível de risco ou por sensor"],
                            ["/indicadores", "GET", "Calcula total de leituras, quantidade e percentual de alertas, média, mínimo e máximo"],
                            ["/locais", "GET", "Devolve cada local monitorado com a última leitura, a frase de orientação e o que fazer"],
                            ["/relatos", "POST e GET", "Recebe e lista relatos de vizinhos, limpando o texto e detectando urgência"],
                            ["/padrao-horario", "GET", "Mostra o risco médio por hora do dia e destaca a melhor faixa para atividades ao ar livre"],
                            ["/health", "GET", "Informa se a central e os modelos estão funcionando"],
                        ],
                        "col_widths": [34, 24, 122],
                    }
                ],
            },
            {
                "title": "3. CENÁRIOS DE TESTE E LIMITES",
                "tables": [
                    {
                        "headers": ["Cenário", "Entrada enviada", "Resposta da central"],
                        "rows": [
                            ["Ar bom na UBS", "Gases 706, CO 925, 18 °C, 55% umidade", "Aceito com 201, nível normal, gravado no CSV"],
                            ["Ar carregado na praça", "Gases 980, CO 1120, 24 °C, 42% umidade", "Aceito com 201, nível atenção e alerta ativo"],
                            ["Ar ruim na escola", "Gases 1280, CO 1383, 31 °C, 34% umidade", "Aceito com 201, nível crítico e alerta ativo"],
                            ["Leitura incompleta", "Mensagem sem o campo de valor", "Recusado com erro 400 e nada gravado"],
                        ],
                        "col_widths": [42, 68, 70],
                    }
                ],
                "body": [
                    "Todas as capturas abaixo foram tiradas com a central ligada de verdade: os três cenários do sensor, um envio manual aceito, envios inválidos recusados, as linhas gravadas no CSV e os indicadores calculados. O projeto também conta com 24 testes automáticos cobrindo rotas, validação e segurança.",
                    "Limites conhecidos: se os arquivos de modelo de IA não estiverem presentes, a central continua funcionando normalmente pela regra de limiar. Além disso, gravar em CSV é ótimo para abrir numa planilha, mas não aguenta muitos sensores escrevendo ao mesmo tempo. Para atender vários bairros simultaneamente, a central sobe para a nuvem com banco PostgreSQL. O sistema apoia os ODS 3 e 11.",
                ],
            },
            {
                "title": "4. A CENTRAL RODANDO",
                "images": [
                    {"path": str(evid / "05_cenarios.png"), "caption": "Figura 2: Os três cenários enviados pelo script do sensor para a central.", "width": 160},
                    {"path": str(evid / "05_post.png"), "caption": "Figura 3: Envio válido aceito com 201; leituras sem valor ou com data no futuro recusadas com 400.", "width": 160},
                    {"path": str(evid / "05_csv_indicadores.png"), "caption": "Figura 4: Linhas salvas no CSV com data e hora, consulta filtrando ar ruim e indicadores calculados.", "width": 160},
                    {"path": str(evid / "05_codigo.png"), "caption": "Figura 5: Trechos principais do código: dicionário de limiares, decisão condicional, gravação no CSV e cálculo de indicadores.", "width": 160},
                ],
            },
        ],
    }

    # 06 - Machine Learning
    doc06 = {
        "title": "RESPIRACIDADÃO: O MODELO DA CENTRAL",
        "subtitle": ["Como a central decide se o ar está bom, carregado ou ruim", "Resumo técnico que acompanha a apresentação"],
        "meta": meta("Machine Learning & Modelling"),
        "output_dir": str(DOCS_DIR / "06-machine-learning-and-modelling"),
        "filename": "06_RespiraCidadao_ML_Resumo",
        "sections": [
            {
                "title": "1. DADOS E OBJETIVO",
                "body": [
                    f"Usamos a base pública real UCI Air Quality, com {mil(STATS['dataset']['registros_brutos'])} horas medidas numa cidade italiana. Depois de retirar as horas em que o sensor falhou, marcadas com -200, ficaram {mil(STATS['dataset']['registros_limpos'])} horas completas.",
                    "Queremos prever o nível do ar definido pelo monóxido de carbono medido em laboratório: abaixo de 1,5 mg/m³ é bom, até 3,0 é carregado e acima disso é ruim. Para não criar uma solução impossível na prática, o modelo só recebe as quatro medidas que nosso sensor barato consegue ler: dois sensores de gás, temperatura e umidade. O valor de laboratório nunca entra como entrada, evitando vazamento de resposta.",
                    "Separamos 80% das horas para treino e 20% para teste antes de qualquer ajuste, mantendo a mesma proporção de níveis nos dois grupos. Juntamos a padronização de escala e o modelo num mesmo fluxo de processamento para garantir que o conjunto de teste nunca influencie o preparo dos dados. O trabalho apoia os ODS 3, 10 e 11.",
                ],
                "images": [{"path": str(ml_charts / "01_eda_classes_box.png"), "caption": "Figura 1: Quantidade de horas em cada nível e como a leitura de gases se separa entre eles."}],
            },
            {
                "title": "2. SEIS MODELOS NO MESMO TESTE",
                "tables": [
                    {
                        "headers": ["Modelo", "Acerto no treino", "Acerto no teste", "F1-macro no teste", "Diferença"],
                        "rows": [
                            [
                                r["modelo"]
                                .replace(" (baseline)", ", referência linear")
                                .replace(" (default)", ", padrão sem ajuste")
                                .replace(" (k=15)", ", 15 vizinhos")
                                .replace(" (depth=8)", ", profundidade 8")
                                .replace(" (tuned, CV=5)", ", ajustada com validação cruzada"),
                                pct(r["train_acc"]),
                                pct(r["test_acc"]),
                                pct(r["test_f1_macro"]),
                                f"{r['gap_overfit'] * 100:+.1f} pp".replace(".", ","),
                            ]
                            for r in ML["comparacao_modelos"]
                        ],
                        "col_widths": [68, 26, 26, 30, 30],
                    }
                ],
                "body": [
                    f"A Random Forest sem ajuste decorou os dados de treino, chegando a 100%, mas caiu no teste. Fizemos uma busca aleatória de ajustes com validação cruzada em cinco partes do treino, atingindo F1-macro médio de {num(ML['cv_f1_macro'], 3)}. O modelo final ficou com {pct(ML['teste_accuracy'])} de acerto no teste e apenas 1,5 ponto percentual de diferença para o treino, usando 250 árvores de profundidade máxima 8 e pelo menos 16 horas por folha para impedir que ele decore casos isolados.",
                    "A regressão logística acertou duas horas a mais em 1.389, um empate técnico. Escolhemos a Random Forest porque sensores de gás reagem de forma não linear quando o calor e a umidade mudam, e a floresta aprende essas combinações naturalmente. O peso de cada medida na decisão ficou assim: " + ", ".join(f"{FI_NOME[f['feature']]} com {pct(f['importance'])}" for f in ML["feature_importance"]) + ".",
                ],
                "images": [{"path": str(ml_charts / "02_confusao_feature_importance.png"), "caption": "Figura 2: Onde o modelo erra no teste e quanto cada medida pesa na decisão."}],
            },
            {
                "title": "3. POR QUE USAR SÓ AS MEDIDAS DO SENSOR",
                "tables": [
                    {
                        "headers": ["Abordagem", "Acertos em 100 horas", "Funciona num bairro comum?"],
                        "rows": [
                            ["Regra simples direto no sensor", f"{regra['accuracy'] * 100:.0f}", "Sim, inclusive sem internet"],
                            ["Modelo com as 4 medidas do sensor", f"{campo['accuracy'] * 100:.0f}", "Sim"],
                            ["Modelo com 11 medidas de laboratório", f"{lab['accuracy'] * 100:.0f}", "Não, exige estação oficial cara"],
                            ["4 medidas testadas em meses inéditos", f"{ML['split_temporal_accuracy'] * 100:.0f}", "É o número mais honesto para o uso real"],
                        ],
                        "col_widths": [76, 44, 60],
                    }
                ],
                "body": [
                    f"Nas {mil(ml_teste)} horas de teste, nenhuma hora de ar bom foi confundida com ar ruim, nem o contrário. Todos os erros ficaram entre níveis vizinhos.",
                    f"A última linha da tabela é o teste mais exigente. No sorteio comum, o modelo pode ver horas muito próximas no tempo durante o treino. No teste temporal, ele treinou nos primeiros 80% do calendário e foi avaliado nos 20% finais, meses completamente inéditos. O acerto foi de {campo['accuracy'] * 100:.0f}% para {ML['split_temporal_accuracy'] * 100:.0f}%, e é essa transparência que levamos para quem instala o aparelho.",
                ],
            },
            {
                "title": "4. USO NO APLICATIVO E LIMITES",
                "tables": [
                    {
                        "headers": ["Leitura nunca vista pelo modelo", "Veredito", "Confiança"],
                        "rows": [
                            [d["cenario"], NIVEL[d["classe_predita"]], conf(max(d["probabilidades"].values()))]
                            for d in ML["demonstracao_nao_vista"]
                        ],
                        "col_widths": [90, 45, 45],
                    }
                ],
                "body": [
                    "A central roda esse modelo a cada leitura recebida e o aplicativo traduz o resultado numa frase direta: \"A central conferiu e concorda: Ruim, com 93% de confiança.\" Se houver discordância com a luz local do sensor, o app recomenda seguir o nível mais cuidadoso.",
                    "Limite principal: os dados vieram de outro país e outro clima. Antes de operar num bairro novo, o sensor precisa passar algumas semanas ao lado de uma estação oficial da CETESB para recalibrar. Sensores de gás também envelhecem e exigem troca periódica.",
                ],
            },
        ],
    }

    # 07 - Cloud
    doc07 = {
        "title": "RESPIRACIDADÃO: A CENTRAL NA NUVEM",
        "subtitle": ["Função sob demanda, banco gerenciado e IA de texto na AWS", "AWS Lambda, CloudWatch, Hugging Face e Amazon RDS PostgreSQL"],
        "meta": meta("Plataformas, Serviços Cognitivos & Cloud Computing"),
        "output_dir": str(DOCS_DIR / "07-plataformas-servicos-cognitivos-cloud"),
        "filename": "07_RespiraCidadao_Cloud_Serverless",
        "sections": [
            {
                "title": "1. CENÁRIO, ARQUITETURA E LIMIARES",
                "body": [
                    "Uma prefeitura não quer manter um servidor ligado o dia inteiro em cada bairro esperando uma queimada. Por isso, levamos a central do RespiraCidadão para uma arquitetura serverless na AWS: a função AWS Lambda só roda nos instantes em que chega uma leitura pelo endereço público. Ela valida os dados, classifica o nível de risco, aciona a análise de texto quando existe relato de morador e grava o registro num banco PostgreSQL gerenciado no Amazon RDS. Cada passo fica registrado nos logs do Amazon CloudWatch.",
                    "O sistema beneficia coordenações de escolas públicas, postos de saúde e famílias com crianças, idosos ou pessoas com asma na periferia. Atende ao ODS 3 ao avisar antes da crise respiratória, ao ODS 10 ao usar sensores acessíveis fora das áreas nobres e ao ODS 11 ao abrir dados ambientais por bairro.",
                    "Os limiares de risco funcionam localmente na função, sem depender de serviço externo: para fumaça e gases, atenção a partir de 830 e crítico a partir de 1140; para monóxido de carbono, atenção a partir de 1010 e crítico a partir de 1280. São os mesmos números do sensor ESP32 e da API local.",
                    "Para que a função acesse a API externa de inteligência artificial sem precisar pagar por um tradutor de rede privado na AWS, ela roda fora de uma rede fechada. O banco PostgreSQL responde apenas na porta 5432, exige usuário, senha guardada em variável de ambiente e criptografia SSL em toda conexão, além de manter o disco cifrado. Todas as gravações usam consultas parametrizadas, impedindo injeção de SQL. Em operação permanente de uma prefeitura, função e banco entrariam juntos numa rede privada corporativa.",
                ],
                "tables": [
                    {
                        "headers": ["Recurso publicado na AWS", "Endereço e configuração"],
                        "rows": [
                            ["Function URL da Lambda", "https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws/"],
                            ["Banco RDS PostgreSQL 18.3", "respiracidadao-db.co6giv33mf2r.us-east-1.rds.amazonaws.com, porta 5432, banco respiracidadao, sem senha exposta"],
                            ["Logs no CloudWatch", "/aws/lambda/respiracidadao-central"],
                            ["Rotas publicadas", "GET /health verifica o estado; POST /ocorrencias valida, classifica e grava devolvendo 201 ou 400; GET /ocorrencias lista as 20 leituras mais recentes"],
                        ],
                        "col_widths": [48, 132],
                    }
                ],
            },
            {
                "title": "2. CAMADA DE IA E RESILIÊNCIA NA PRÁTICA",
                "body": [
                    "Escolhemos a API da Hugging Face com o modelo multilíngue cardiffnlp/twitter-xlm-roberta-base-sentiment, chamado diretamente pela biblioteca padrão do Python no endereço atual router.huggingface.co, usando o token cadastrado apenas nas variáveis de ambiente da Lambda. Nenhuma senha ou chave fica escrita no código.",
                    "Por que não usamos o Amazon Comprehend: testamos a permissão dele diretamente na conta do AWS Academy Learner Lab e o ambiente bloqueou a chamada por falta de permissão de IAM. Nosso código suporta os dois provedores, mas a Hugging Face funcionou sem barreiras de permissão e entende bem o português coloquial usado em relatos de moradores.",
                    "A resiliência foi comprovada ao vivo na AWS. Com o token configurado e a função saindo para a internet, cada relato do simulador dispara a chamada HTTPS real para a Hugging Face. Como a cota gratuita mensal da conta de testes já estava esgotada, a API externa respondeu com erro 402 de limite de créditos. A função capturou a resposta, registrou um aviso claro no CloudWatch e concluiu normalmente a classificação de risco e a gravação no banco. Numa queimada real, a falha de um serviço externo de texto nunca pode impedir o alerta nem apagar o registro do sensor.",
                ],
            },
            {
                "title": "3. TESTE PONTA A PONTA NA AWS E EVIDÊNCIAS",
                "body": [
                    "Além dos 8 testes automatizados rodando localmente sem AWS, validamos o fluxo completo direto na nuvem: consulta de saúde da função, recusa com erro 400 para leitura sem valor, cenário normal na UBS, cenário de queimada perto da escola subindo de normal para atenção e crítico com disparo de alerta, verificação dos logs no CloudWatch e consulta direta das 15 ocorrências gravadas no banco RDS.",
                ],
                "images": [
                    {"path": str(evid / "07_aws_lambda_env.png"), "caption": "Figura 1: Variáveis de ambiente da função na AWS, incluindo a chave da Hugging Face e os dados do banco, com as senhas ocultadas por segurança.", "width": 162},
                    {"path": str(evid / "07_aws_simulador.png"), "caption": "Figura 2: Simulador Python enviando leituras reais para a Function URL, testando erro 400, cenário normal, escalada de queimada e consulta do histórico.", "width": 162},
                    {"path": str(evid / "07_aws_cloudwatch.png"), "caption": "Figura 3: Logs no Amazon CloudWatch exibindo o payload recebido, o aviso da chamada resiliente à Hugging Face, o alerta crítico e a confirmação de gravação no RDS.", "width": 162},
                    {"path": str(evid / "07_aws_rds_console.png"), "caption": "Figura 4: Painel do Amazon RDS confirmando o banco PostgreSQL ativo, cifrado e com acesso controlado na porta 5432.", "width": 162},
                    {"path": str(evid / "07_aws_rds_select.png"), "caption": "Figura 5: Consulta SQL direta no Amazon RDS exibindo as ocorrências gravadas e o resumo por sensor.", "width": 162},
                ],
            },
        ],
    }

    # 08 - Redes Neurais
    doc08 = {
        "title": "RESPIRACIDADÃO: A SEGUNDA OPINIÃO",
        "subtitle": ["Rede neural em PyTorch que confere o veredito da central", "Desenvolvimento completo nas 8 etapas do projeto"],
        "meta": meta("Redes Neurais Artificiais, Deep Learning e Algoritmos Genéticos"),
        "output_dir": str(DOCS_DIR / "08-redes-neurais-deep-learning-ag"),
        "filename": "08_RespiraCidadao_Redes_Neurais",
        "sections": [
            {
                "title": "1. ETAPAS 1 A 4: PROBLEMA, DADOS, PREPARO E ARQUITETURA",
                "bullets": [
                    {"text": "Etapa 1, problema: classificar o ar como bom, carregado ou ruim a partir das 4 medidas do sensor para avisar escolas e postos de saúde antes de crises respiratórias, apoiando os ODS 3 e 11.", "level": 0},
                    {"text": f"Etapa 2, dados: base pública real UCI Air Quality com {mil(STATS['dataset']['registros_limpos'])} horas completas, sem nenhum dado sintético.", "level": 0},
                    {"text": "Etapa 3, preparo: divisão estratificada em 70% para treino, 15% para validação e 15% para teste, padronizando as medidas usando apenas a estatística do treino.", "level": 0},
                    {"text": "Etapa 4, arquitetura: rede densa simples do tipo MLP com 4 entradas, camadas ocultas de 64 e 32 neurônios com normalização e desligamento aleatório de 25%, e 3 saídas. Como cada leitura traz apenas 4 números por hora, sem imagem nem sequência longa, redes convolucionais ou recorrentes seriam exagero para este formato.", "level": 0},
                ],
            },
            {
                "title": "2. ETAPAS 5 A 7: TREINO, REGULARIZAÇÃO E AVALIAÇÃO",
                "tables": [
                    {
                        "headers": ["Experimento", "Épocas", "Acerto no treino", "Acerto no teste", "F1-macro", "Diferença"],
                        "rows": [
                            [
                                r["modelo"]
                                .replace(" (gas_voc)", ", direto no sensor")
                                .replace(" (128-64, sem regularização)", ", 128 e 64 neurônios sem freios")
                                .replace(" (64-32, BN + Dropout + ES)", ", 64 e 32 neurônios regularizada"),
                                str(r["epocas"]),
                                pct(r["train_acc"]) if r["train_acc"] is not None else "sem treino",
                                pct(r["test_acc"]),
                                pct(r["test_f1_macro"]),
                                f"{r['gap'] * 100:.1f} pp".replace(".", ",") if r["gap"] is not None else "não se aplica",
                            ]
                            for r in NN["comparacao_experimentos"]
                        ],
                        "col_widths": [58, 16, 28, 28, 22, 28],
                    }
                ],
                "images": [
                    {"path": str(nn_charts / "01_curvas_treinamento.png"), "caption": "Figura 1: Evolução da perda e do acerto por época, comparando a rede sem freios com a rede regularizada."},
                    {"path": str(nn_charts / "02_matriz_confusao_nn.png"), "caption": "Figura 2: Matriz de confusão da rede regularizada no conjunto de teste."},
                ],
                "body": [
                    f"Na primeira tentativa, treinamos uma rede maior de 128 e 64 neurônios sem nenhuma regularização durante 150 épocas. A perda de validação atingiu o melhor ponto na época 41 e depois começou a piorar enquanto o treino continuava melhorando, deixando {num(nn_base['gap'] * 100, 1)} pontos de diferença entre treino e teste. Era sinal claro de que a rede estava decorando os dados.",
                    f"Na rede B, reduzimos para 64 e 32 neurônios e aplicamos quatro freios contra memorização: normalização entre camadas para estabilizar o treino, desligamento aleatório de 25% dos neurônios a cada passo para evitar dependência de poucos caminhos, penalização de pesos altos e parada antecipada quando a validação passa 15 épocas sem melhorar. O treino parou na época {NN['epocas_executadas']}, recuperou o melhor estado da época {NN['melhor_epoca']} e chegou a {pct(nn_reg['test_acc'])} no teste com apenas {num(nn_reg['gap'] * 100, 1)} ponto de diferença para o treino.",
                    f"Nas {mil(nn_teste)} horas de teste, nenhuma hora de ar bom foi classificada como ruim, nem o inverso. Comparada à regra simples do sensor, a rede neural ganha {dec(format((nn_reg['test_acc'] - nn_regra['test_acc']) * 100, '.1f'))} pontos percentuais de acerto.",
                ],
            },
            {
                "title": "3. ETAPA 8: DEMONSTRAÇÃO, LIMITES E RESPONSABILIDADE",
                "tables": [
                    {
                        "headers": ["Leitura nunca vista", "Veredito", "Probabilidade: Bom / Carregado / Ruim"],
                        "rows": [
                            [
                                d["cenario"],
                                NIVEL[d["classe_predita"]],
                                " / ".join(pct(d["probabilidades"][k]) for k in ("normal", "atencao", "critico")),
                            ]
                            for d in NN["demonstracao_nao_vista"]
                        ],
                        "col_widths": [66, 30, 84],
                    }
                ],
                "body": [
                    "No produto final, a Random Forest confere cada leitura que chega do sensor e a rede neural atua como segunda opinião na tela Como funciona, permitindo comparar ao vivo a luz do sensor, o modelo principal e a rede neural para qualquer combinação de valores.",
                    "Limites: a base vem de outra cidade e exige recalibração local antes de uso real em um bairro novo. Como próximo passo, pretendemos testar redes recorrentes lendo janelas de várias horas seguidas para prever a piora do ar antes mesmo de ela atingir o nível crítico.",
                ],
                "bullets": [
                    {"text": "Acessibilidade: o usuário vê cor e palavra simples, nunca probabilidades cruas.", "level": 0},
                    {"text": "Segurança: as entradas são validadas antes de chegar à rede e os pesos são carregados em modo seguro que bloqueia execução de código malicioso.", "level": 0},
                    {"text": "Privacidade: a rede recebe apenas quatro números ambientais, sem qualquer dado pessoal.", "level": 0},
                    {"text": "Sustentabilidade: treina em segundos num computador comum e o arquivo salvo ocupa apenas 17 KB.", "level": 0},
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
        "subtitle": ["O sensor barato consegue explicar o monóxido real?", "Análise inferencial e preditiva sobre a base real UCI Air Quality"],
        "meta": meta("Statistical Computing with R & Python"),
        "output_dir": str(DOCS_DIR / "09-statistical-computing-r-python"),
        "filename": "09_RespiraCidadao_Relatorio_Estatistico",
        "sections": [
            {
                "title": "1. A PERGUNTA E A BASE DE DADOS",
                "body": [
                    "Cliente: uma secretaria municipal que precisa monitorar a qualidade do ar em escolas e postos de saúde sem o custo de instalar estações laboratoriais em cada bairro. Pergunta central: as medições de um sensor barato explicam bem o monóxido de carbono que uma estação oficial registraria? Se a resposta for sim, podemos emitir alertas confiáveis a baixo custo, apoiando os ODS 3 e 11.",
                    f"Usamos a base pública real UCI Air Quality, publicada pela Universidade da Califórnia em Irvine. Ela traz {mil(STATS['dataset']['registros_brutos'])} horas em que sensores baratos de óxido metálico operaram lado a lado com um analisador oficial de referência. Retirando as horas com código de falha -200, restaram {mil(STATS['dataset']['registros_limpos'])} medições completas.",
                    f"Pelo monóxido de referência CO(GT), a base se divide em {mil(STATS['dataset']['distribuicao_risco']['normal'])} horas de ar bom abaixo de 1,5 mg/m³, {mil(STATS['dataset']['distribuicao_risco']['atencao'])} horas carregadas entre 1,5 e 3,0 mg/m³ e {mil(STATS['dataset']['distribuicao_risco']['critico'])} horas de ar ruim a partir de 3,0 mg/m³.",
                ],
            },
            {
                "title": "2. DISTRIBUIÇÃO NORMAL E TESTES DE HIPÓTESE",
                "tables": [
                    {
                        "headers": ["Item", "Pergunta", "Resultado", "Decisão"],
                        "rows": [
                            ["02a", "P(X < média) de CO(GT)", f"{pct(it2['p_menor_media'], 2)}, com média de {num(it2['media'], 4)} mg/m³", it2["classificacao_a"]],
                            ["02b", "P(X > mediana) de CO(GT)", f"{pct(it2['p_maior_mediana'], 2)}, com mediana de {num(it2['mediana'], 1)} mg/m³", it2["classificacao_b"]],
                            ["03a", "Teste à esquerda, n=20, alfa=6%", f"Média amostral {num(t3a['media_amostral'])}, Z={num(t3a['z_calculado'], 4)}, Z crítico {num(t3a['z_critico'], 4)}, p={num(t3a['p_valor'], 4)}", t3a["decisao"]],
                            ["03b", "Teste à direita, n=25, alfa=9%", f"Média amostral {num(t3b['media_amostral'])}, Z={num(t3b['z_calculado'], 4)}, Z crítico {num(t3b['z_critico'], 4)}, p={num(t3b['p_valor'], 4)}", t3b["decisao"]],
                        ],
                        "col_widths": [14, 50, 72, 44],
                    }
                ],
                "body": [
                    f"A média de 2,18 mg/m³ fica acima da mediana de 1,9 mg/m³ porque existem picos altos de poluição puxando a cauda direita da distribuição. Por isso, sob a curva Normal, a probabilidade de ficar acima da mediana dá 57,8% e não 50%. As {mil(STATS['dataset']['distribuicao_risco']['critico'])} horas críticas representam quase uma em cada quatro horas medidas, que é justamente a faixa em que o alerta faz diferença.",
                    f"Nos dois testes Z, usamos a média populacional de {num(it3['media_pop'], 4)} mg/m³ e o desvio padrão populacional de {num(it3['sigma_pop'], 4)} mg/m³. Em ambos os casos não rejeitamos H0: as médias sorteadas ficaram do lado oposto ao da hipótese alternativa, gerando valores p altos, exatamente o esperado para amostras tiradas da mesma população.",
                ],
                "images": [{"path": str(stats_charts / "02_distribuicao_normal_co.png"), "caption": "Figura 1: Distribuição real de CO(GT) comparada à curva Normal equivalente."}],
            },
            {
                "title": "3. UM SENSOR SÓ: REGRESSÃO LINEAR SIMPLES",
                "body": [
                    "a) O gráfico de dispersão entre o sensor de monóxido PT08.S1(CO) e o valor de laboratório CO(GT) forma uma nuvem estreita e ascendente: quando o sensor barato sobe, o monóxido real sobe junto.",
                    f"b) A covariância é {num(it4['covariancia'], 2)} e a correlação de Pearson chega a r = {num(it4['pearson_r'], 3)}, com p < 0,0001, indicando relação positiva e forte.",
                    "c) Agrupando os dados por decis, a média do monóxido real sobe de forma praticamente linear a cada faixa do sensor.",
                    f"d) Equação ajustada: {dec(it4['equacao'])}.",
                    f"e) O coeficiente de determinação R² chegou a {pct(it4['r2'], 2)} com teste F = {num(it4['teste_f'], 2)} e p < 0,0001. Um único sensor barato já explica mais de três quartos da variação do gás real.",
                    f"f) Previsão de exemplo: com o sensor marcando 1350, o monóxido previsto é {num(it4['previsao_exemplo']['co_previsto'], 3)} mg/m³, já em nível ruim.",
                ],
                "images": [
                    {"path": str(stats_charts / "04_dispersao_regressao_simples.png"), "caption": "Figura 2: Dispersão entre o sensor barato e o analisador oficial com a reta ajustada."},
                    {"path": str(stats_charts / "04_correlacao_bivariada.png"), "caption": "Figura 3: Evolução da média de CO(GT) por decis do sensor."},
                ],
            },
            {
                "title": "4. AS QUATRO MEDIDAS DO SENSOR: REGRESSÃO MÚLTIPLA",
                "body": [
                    "Aqui combinamos exatamente as quatro variáveis disponíveis no nosso ESP32: os dois sensores de gás PT08.S1(CO) e PT08.S2(NMHC), a temperatura T e a umidade relativa RH.",
                    f"a) e b) Os dois sensores de gás caminham forte com o monóxido oficial, com r = {num(corr['CO(GT)']['PT08.S1(CO)'], 3)} e {num(corr['CO(GT)']['PT08.S2(NMHC)'], 3)}, e também entre si, com r = {num(corr['PT08.S1(CO)']['PT08.S2(NMHC)'], 3)}. Temperatura e umidade quase não explicam o gás sozinhas, mas se relacionam fortemente entre si com r = {num(corr['T']['RH'], 3)} e compensam a sensibilidade dos sensores de gás ao clima.",
                    f"c) Na matriz de correlação, os três medidores de gases formam o bloco mais forte, enquanto temperatura e umidade mostram a única relação negativa acentuada, refletindo tardes quentes e secas.",
                    f"d) Equação múltipla: {dec(it5['equacao'])}.",
                    f"e) O R² saltou para {pct(it5['r2'], 2)}, com R² ajustado de {pct(it5['r2_ajustado'], 2)} e teste F = {num(it5['teste_f'], 2)} com p < 0,0001. Somar as quatro medidas leva a explicação de 77% para 88%. Como os dois sensores de gás são altamente correlacionados entre si, seus coeficientes devem ser lidos em conjunto, não como efeitos isolados.",
                    f"f) Previsões de exemplo: em {it5['previsoes'][0]['cenario']}, com {ent(it5['previsoes'][0]['entrada'])}, a previsão é {num(it5['previsoes'][0]['co_previsto'], 3)} mg/m³, nível carregado. Em {it5['previsoes'][1]['cenario']}, com {ent(it5['previsoes'][1]['entrada'])}, sobe para {num(it5['previsoes'][1]['co_previsto'], 3)} mg/m³, nível ruim.",
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
                    {"path": str(stats_charts / "05_dispersao_multivariada.png"), "caption": "Figura 4: Relação individual de cada variável do sensor com o monóxido oficial."},
                    {"path": str(stats_charts / "05_matriz_correlacao.png"), "caption": "Figura 5: Matriz de correlação de Pearson entre as variáveis."},
                ],
            },
            {
                "title": "5. AR RUIM OU NÃO: REGRESSÃO LOGÍSTICA BINÁRIA",
                "body": [
                    f"a) Modelamos a probabilidade P de o ar estar ruim, definido como CO(GT) a partir de 3,0 mg/m³. Equação do logit: {dec(it6['equacao_logit'])}, convertida em probabilidade pela função sigmoide. Separamos 75% das horas para treino, {mil(STATS['dataset']['registros_limpos'] - sum(sum(l) for l in mc))} registros, e testamos nas {mil(sum(sum(l) for l in mc))} horas restantes.",
                    f"b) No teste, o modelo reconheceu {mil(mc[0][0])} horas sem ar ruim e {mc[1][1]} horas críticas, gerando {mc[0][1]} alarmes falsos e deixando passar {mc[1][0]} horas críticas. A acurácia ficou em {pct(it6['acuracia_teste'], 2)}, com precisão de {pct(it6['precision_critico'], 2)} e sensibilidade de {pct(it6['recall_critico'], 2)}. De cada 100 horas críticas, o modelo captura 86.",
                    f"c) Em dois cenários de exemplo: {it6['classificacoes_exemplo'][0]['cenario']} resultou em {pct(it6['classificacoes_exemplo'][0]['prob_critico'], 2)} de chance de ar ruim, classe 0. Já {it6['classificacoes_exemplo'][1]['cenario']} resultou em {pct(it6['classificacoes_exemplo'][1]['prob_critico'], 2)}, classe 1.",
                ],
                "images": [{"path": str(stats_charts / "06_matriz_confusao_logistica.png"), "caption": "Figura 6: Matriz de confusão da regressão logística no conjunto de teste."}],
            },
            {
                "title": "6. RECOMENDAÇÕES FINAIS",
                "bullets": [
                    {"text": f"O sensor de baixo custo é viável para alertar o bairro: as quatro medidas juntas explicam {pct(it5['r2'], 0)} da variação do monóxido real e acertam {pct(it6['acuracia_teste'], 0)} das horas na detecção de ar ruim.", "level": 0},
                    {"text": "Sempre instale o kit com as quatro medidas. Temperatura e umidade parecem fracas sozinhas, mas corrigem o desvio dos sensores de gás e elevam o R² de 77% para 88%.", "level": 0},
                    {"text": "Mantenha o aviso luminoso local na parede para que a escola continue protegida mesmo quando a internet cair.", "level": 0},
                    {"text": "Recalibre o conjunto em cada bairro novo mantendo o aparelho algumas semanas ao lado de uma estação oficial da CETESB, ajustando os coeficientes ao clima local.", "level": 0},
                ],
            },
        ],
    }

    for doc in [doc01, doc02, doc03, doc05, doc06, doc07, doc08, doc09]:
        render_doc(doc)
        print(f"[OK] Gerado DOCX + PDF: {doc['output_dir']}/{doc['filename']}.pdf")


if __name__ == "__main__":
    build_all()
