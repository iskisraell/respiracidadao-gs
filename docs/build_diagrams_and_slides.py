#!/usr/bin/env python3
"""Desenha o caminho da informação (PNG) e monta os slides do modelo de classificação (PPTX)."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
ML = json.loads((ROOT / "packages" / "ml-modelling" / "artifacts" / "ml_metrics.json").read_text(encoding="utf-8"))

# Mesmas cores do app.
BG, SURFACE, INK, MUTED, LINE = "#f6f5f1", "#ffffff", "#17201f", "#5b6664", "#e3e1da"
BRAND, NORMAL, ATENCAO, CRITICO = "#0f6b66", "#1f8a52", "#b67400", "#c8372d"


def build_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 6.6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    ax.text(0.3, 6.25, "RespiraCidadão: o caminho de uma leitura", fontsize=16, fontweight="bold", color=INK)
    ax.text(0.3, 5.88, "Do sensor na parede da escola até a frase no celular da diretora.", fontsize=10.5, color=MUTED)

    def box(x, y, w, h, n, title, lines, tech, edge=BRAND):
        ax.add_patch(patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.16",
                                            linewidth=1.4, edgecolor=LINE, facecolor=SURFACE))
        ax.add_patch(patches.Rectangle((x + 0.1, y + h - 0.02), w - 0.2, 0.07, color=edge))
        ax.text(x + 0.18, y + h - 0.32, f"{n}. {title}", fontsize=11.5, fontweight="bold", color=INK, va="top")
        ax.text(x + 0.18, y + h - 0.72, "\n".join(lines), fontsize=9, color=INK, va="top", linespacing=1.45)
        ax.text(x + 0.18, y + 0.18, tech, fontsize=7.6, color=MUTED, va="bottom", style="italic")

    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=BRAND, lw=1.6, shrinkA=2, shrinkB=2))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.17, label, ha="center", fontsize=8, color=BRAND, fontweight="bold")

    box(0.3, 3.0, 3.4, 2.4, 1, "Sensor no lugar", [
        "Mede fumaça, monóxido,", "temperatura e umidade.", "Acende verde, amarelo ou",
        "vermelho e apita, mesmo", "sem internet.",
    ], "ESP32 + DHT22 + 2 sensores de gás + LEDs + buzzer", edge=NORMAL)
    box(4.3, 3.0, 3.4, 2.4, 2, "Central", [
        "Confere a leitura com o que", "aprendeu em 6.941 horas reais.", "Guarda tudo com selo digital",
        "e barra quem tenta inundar", "o sistema.",
    ], "FastAPI + SQLite/CSV, ou Lambda + PostgreSQL na nuvem")
    box(8.3, 3.0, 3.4, 2.4, 3, "App", [
        "A pessoa escolhe o lugar e vê", "a cor, uma frase e o que fazer.", "Mostra o melhor horário",
        "e o que os vizinhos", "estão relatando.",
    ], "React + TypeScript, celular e computador", edge=CRITICO)

    arrow(3.75, 4.2, 4.25, 4.2, "leitura")
    arrow(7.75, 4.2, 8.25, 4.2, "nível + frase")

    box(0.3, 0.3, 5.4, 2.2, 4, "O que a central aprendeu", [
        "Base real de 6.941 horas de uma estação de referência.",
        f"Acerta {round(ML['teste_accuracy'] * 100)} de cada 100 horas usando só as 4 medidas do sensor.",
        "Uma segunda opinião (rede neural) confirma o veredito.",
    ], "Random Forest + rede neural PyTorch; estatística sobre a mesma base", edge=ATENCAO)
    box(6.3, 0.3, 5.4, 2.2, 5, "Vizinhos e padrão do dia", [
        "Relato sem nome nem localização; urgência detectada.",
        "Padrão por hora: ar ruim em 19% das horas entre 14h e 17h,",
        "contra 63% às 19h. Daí sai a dica de horário.",
    ], "POST /relatos, GET /padrao-horario", edge=ATENCAO)

    arrow(3.0, 2.55, 5.4, 2.95)
    ax.text(1.55, 2.72, "modelo treinado", fontsize=8, color=BRAND, fontweight="bold", va="center")
    arrow(9.0, 2.55, 9.0, 2.95)
    ax.text(9.12, 2.7, "dica e relatos", fontsize=8, color=BRAND, fontweight="bold", va="center")

    fig.tight_layout()
    out = ASSETS_DIR / "arquitetura_uml_respiracidadao.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Diagrama gerado em {out}")


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def build_ml_slides():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    def new_slide(title, subtitle=""):
        s = prs.slides.add_slide(blank)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(BG)
        bar = s.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = rgb(BRAND)
        bar.line.fill.background()
        tb = s.shapes.add_textbox(Inches(0.7), Inches(0.4), Inches(11.9), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        r = tf.paragraphs[0].add_run()
        r.text = title
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = "Montserrat", Pt(28), True, rgb(INK)
        if subtitle:
            r2 = tf.add_paragraph().add_run()
            r2.text = subtitle
            r2.font.name, r2.font.size, r2.font.color.rgb = "Montserrat", Pt(14), rgb(BRAND)
        return s

    def bullets(slide, left, top, width, height, items, size=16):
        tf = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height)).text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(12)
            r = p.add_run()
            r.text = f"•  {item}"
            r.font.name, r.font.size, r.font.color.rgb = "Montserrat", Pt(size), rgb(INK)

    acc = ML["teste_accuracy"] * 100
    regra, campo, lab = ML["comparacao_conjuntos"]

    # 1. Capa
    s = new_slide("RespiraCidadão", "Como a central decide se o ar está bom, carregado ou ruim")
    bullets(s, 0.7, 2.2, 11.5, 3.5, [
        "Uma diretora abre o celular às 7h40 e lê: \"Ar ruim perto da escola agora.\" Esta apresentação mostra de onde vem essa frase.",
        "Machine Learning and Modelling | Sala 1TIAPZ1 | Grupo Perceptron",
        "Giovanni Henrique Pereira Hessel (RM 570574), Suellen Pereira da Silva (RM 573862), Israel Carneiro de Toledo (RM 573854)",
    ], size=17)

    # 2. Problema e dados
    s = new_slide("O problema e os dados", "ODS 3 (saúde) e ODS 11 (cidades)")
    bullets(s, 0.7, 1.6, 5.9, 5.3, [
        "Fumaça e trânsito pioram crises de asma em crianças e idosos. Estação oficial é cara e longe da periferia.",
        "Base real: UCI Air Quality, 9.357 horas medidas numa cidade italiana; 6.941 completas depois de tirar falhas de sensor.",
        "Alvo: nível do ar pelo monóxido medido em laboratório (abaixo de 1,5 mg/m³ bom; até 3,0 carregado; acima, ruim).",
        "Entradas: só as 4 coisas que nosso sensor mede. O valor de laboratório nunca entra como entrada.",
    ], size=15)
    s.shapes.add_picture(str(ASSETS_DIR / "arquitetura_uml_respiracidadao.png"), Inches(6.8), Inches(1.7), width=Inches(6.0))

    # 3. EDA
    s = new_slide("Como os dados se distribuem", "2.531 horas de ar bom, 2.718 carregado, 1.692 ruim")
    s.shapes.add_picture(str(ROOT / "packages" / "ml-modelling" / "charts" / "01_eda_classes_box.png"), Inches(0.8), Inches(1.6), width=Inches(11.6))

    # 4. Comparação
    s = new_slide("Seis modelos, mesmo teste", "Treino e teste separados antes de qualquer ajuste; validação cruzada em 5 partes")
    rows = ML["comparacao_modelos"]
    table = s.shapes.add_table(len(rows) + 1, 5, Inches(0.7), Inches(1.7), Inches(11.9), Inches(3.4)).table
    for c, h in enumerate(["Modelo", "Acerto no treino", "Acerto no teste", "F1 médio", "Diferença treino/teste"]):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(BRAND)
        cell.text = h
        f = cell.text_frame.paragraphs[0].font
        f.size, f.bold, f.color.rgb = Pt(13), True, rgb("#ffffff")
    for r_idx, row in enumerate(rows, start=1):
        vals = [row["modelo"], f"{row['train_acc']*100:.1f}%", f"{row['test_acc']*100:.1f}%",
                f"{row['test_f1_macro']*100:.1f}%", f"{row['gap_overfit']*100:+.1f} pp"]
        for c, v in enumerate(vals):
            cell = table.cell(r_idx, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(SURFACE)
            cell.text = v
            f = cell.text_frame.paragraphs[0].font
            f.size, f.color.rgb = Pt(12), rgb(INK)
    bullets(s, 0.7, 5.4, 11.9, 1.8, [
        f"Escolhemos a Random Forest ajustada: {acc:.1f}% no teste e só 1,5 ponto de diferença para o treino. A versão sem ajuste decorava o treino (100%).",
        "A regressão logística ficou 2 horas à frente em 1.389. É empate. Ficamos com a floresta porque o sensor de gás muda de leitura com calor e umidade, e ela aprende essas combinações sozinha.",
        "Ajuste final: 250 árvores, profundidade 8, mínimo de 16 horas por folha e 10 para dividir um nó, todas as 4 medidas em cada divisão. Padronização e modelo ficam num Pipeline, que só aprende com o treino.",
    ], size=14)

    # 5. Matriz e importância
    s = new_slide("Onde ela erra e o que mais pesa", "Nenhuma hora de ar bom virou ar ruim, nem o contrário")
    s.shapes.add_picture(str(ROOT / "packages" / "ml-modelling" / "charts" / "02_confusao_feature_importance.png"), Inches(0.75), Inches(1.6), width=Inches(11.8))

    # 6. Por que só as 4 medidas
    s = new_slide("Por que o modelo usa só o que o sensor mede", "A escolha cabe no equipamento que o bairro pode ter")
    bullets(s, 0.7, 1.7, 11.9, 5.2, [
        f"Regra simples do sensor (sem internet): acerta {regra['accuracy']*100:.0f} de cada 100 horas.",
        f"Modelo com as 4 medidas do sensor: {campo['accuracy']*100:.0f} de cada 100.",
        f"Modelo com 11 medidas de laboratório: {lab['accuracy']*100:.0f} de cada 100. Ganha 1 ponto, mas exige equipamento que nenhum bairro tem.",
        f"Teste no tempo (treina nos meses antigos, testa nos novos): {ML['split_temporal_accuracy']*100:.0f} de cada 100. É o número mais honesto para quem instala hoje.",
    ], size=17)

    # 7. Aplicação e limites
    demo = ML["demonstracao_nao_vista"]
    s = new_slide("No app, na prática", "Três leituras que o modelo nunca viu")
    bullets(s, 0.7, 1.7, 11.9, 5.4, [
        *[f"{d['cenario']}: {d['classe_predita'].replace('atencao', 'carregado').replace('critico', 'ruim').replace('normal', 'bom')}, "
          f"{max(d['probabilidades'].values())*100:.0f}% de confiança." for d in demo],
        "A central roda esse modelo a cada leitura e mostra no app: \"A central conferiu e concorda: Ruim, com 93% de confiança.\"",
        "Limite: os dados são de uma cidade italiana. Em cada bairro novo o sensor fica algumas semanas ao lado de uma estação oficial para recalibrar.",
    ], size=16)

    # 8. Evoluções futuras
    s = new_slide("O que vem depois", "Três passos para o modelo valer em São Paulo")
    bullets(s, 0.7, 1.7, 11.9, 5.2, [
        "Recalibrar com a CETESB: algumas semanas de sensor ao lado de uma estação oficial em cada bairro novo, e o modelo retreinado com esses dados.",
        "Trocar o sensor de gás no prazo: sensores de óxido metálico envelhecem e a leitura deriva. O app avisa quando o sensor passa da validade.",
        "Olhar a série no tempo: um modelo que lê as últimas horas para avisar antes de o ar ficar ruim, não só quando já ficou.",
    ], size=17)

    out_pptx = DOCS_DIR / "06_RespiraCidadao_ML_Slides.pptx"
    prs.save(str(out_pptx))
    print(f"Slides gerados em {out_pptx}")


if __name__ == "__main__":
    build_architecture_diagram()
    build_ml_slides()
