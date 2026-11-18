#!/usr/bin/env python3
"""Gera o diagrama de Arquitetura & UML (PNG) e os Slides PPTX de 06 Machine Learning."""

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


def build_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 6.8))
    fig.patch.set_facecolor("#0f0f12")
    ax.set_facecolor("#0f0f12")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.8)
    ax.axis("off")

    ax.text(
        6.0, 6.4,
        "RespiraCidadão: Arquitetura Integrada CitizenTech e Fluxo de Dados",
        ha="center", va="center", fontsize=14, fontweight="bold", color="#ffffff",
    )
    ax.text(
        6.0, 6.05,
        "Grupo Perceptron (1TIAPZ1) | ODS 3, 10 e 11 | Integração 02 + 03 + 05 + 06 + 07 + 08 + 09",
        ha="center", va="center", fontsize=9.5, color="#acc1cc",
    )

    def box(x, y, w, h, title, lines, edge="#ed145b", fill="#1c1c21", title_col="#ed145b"):
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.14",
            linewidth=1.8, edgecolor=edge, facecolor=fill,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=10, fontweight="bold", color=title_col)
        ax.text(x + w / 2, y + h - 0.56, "\n".join(lines), ha="center", va="top", fontsize=8.3, color="#e5e9f0", linespacing=1.35)

    def arrow(x1, y1, x2, y2, label="", col="#64d2ff"):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8, shrinkA=4, shrinkB=4),
        )
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.16, label, ha="center", va="center",
                    fontsize=7.5, color=col, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#0f0f12", edgecolor="none"))

    # Row 1: Edge -> API -> Storage/Cloud
    box(0.4, 3.6, 2.7, 2.0, "1. Borda IoT (02 AICSS)", [
        "ESP32 Wokwi / Campo",
        "MQ-2 (GPIO 34) + DHT22 (15)",
        "Alerta local: LEDs + Buzzer",
        "Classificação borda (<120/250)",
    ], edge="#00c365", title_col="#00c365")

    box(4.2, 3.6, 3.3, 2.0, "2. API & Segurança (05 + 03)", [
        "FastAPI + Pydantic (HTTP 400/201)",
        "Rate Limit Sliding Window (429)",
        "Sanitização XSS + X-API-Key",
        "SHA-256 Integridade + Auditoria",
    ], edge="#ed145b", title_col="#f35b8d")

    box(8.6, 3.6, 3.0, 2.0, "3. Cloud & Persistência (07)", [
        "AWS Lambda + Function URL",
        "CloudWatch Logs (WARNING)",
        "HF Sentiment Router + Fallback",
        "RDS PostgreSQL / SQLite + CSV",
    ], edge="#ffb700", title_col="#ffb700")

    arrow(3.2, 4.6, 4.1, 4.6, "JSON HTTP", "#00c365")
    arrow(7.6, 4.6, 8.5, 4.6, "HTTPS / DB", "#ffb700")

    # Row 2: Data Science / ML / DL -> Web App
    box(0.4, 0.7, 3.4, 2.1, "4. Estatística Real (09)", [
        "UCI Air Quality (N = 6.941)",
        "Normal P(X<μ), Testes Z (6%/9%)",
        "Reg. Simples (R²=76.9%) &",
        "Múltipla (R²=90.3%) + Logística",
    ], edge="#64d2ff", title_col="#64d2ff")

    box(4.4, 0.7, 3.3, 2.1, "5. IA Preditiva (06 + 08)", [
        "06 ML: Random Forest (89.06%)",
        "08 DL: PyTorch MLP (89.64%)",
        "BatchNorm + Dropout + EarlyStop",
        "Endpoint live POST /predict",
    ], edge="#ed145b", title_col="#f35b8d")

    box(8.4, 0.7, 3.2, 2.1, "6. App Unificado (React + TS)", [
        "Monitor IoT em Tempo Real",
        "Simulador IA (RF vs PyTorch)",
        "Painel Estatístico & Segurança",
        "Identidade Visual FIAP Tokens",
    ], edge="#28cb9c", title_col="#28cb9c")

    arrow(2.1, 2.9, 5.2, 3.5, "Base limpa", "#64d2ff")
    arrow(6.0, 2.9, 6.0, 3.5, "Modelos", "#ed145b")
    arrow(7.6, 3.8, 9.6, 2.9, "REST JSON", "#28cb9c")
    arrow(3.9, 1.75, 4.3, 1.75, "Features", "#64d2ff")
    arrow(7.8, 1.75, 8.3, 1.75, "/predict", "#28cb9c")

    fig.tight_layout()
    out = ASSETS_DIR / "arquitetura_uml_respiracidadao.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Diagrama gerado em {out}")


def build_ml_slides():
    ml = json.loads((ROOT / "packages" / "ml-modelling" / "artifacts" / "ml_metrics.json").read_text(encoding="utf-8"))
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    BG = RGBColor(15, 15, 18)
    CARD = RGBColor(28, 28, 33)
    MAGENTA = RGBColor(237, 20, 91)
    CYAN = RGBColor(100, 210, 255)
    GREEN = RGBColor(0, 195, 101)
    WHITE = RGBColor(255, 255, 255)
    MUTED = RGBColor(172, 193, 204)

    def set_bg(slide):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = BG

    def add_header(slide, title, subtitle=""):
        tb = slide.shapes.add_textbox(Inches(0.7), Inches(0.4), Inches(11.9), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = title
        r.font.name = "Montserrat"
        r.font.size = Pt(26)
        r.font.bold = True
        r.font.color.rgb = WHITE
        if subtitle:
            p2 = tf.add_paragraph()
            r2 = p2.add_run()
            r2.text = subtitle
            r2.font.name = "Montserrat"
            r2.font.size = Pt(13)
            r2.font.color.rgb = MAGENTA

    def add_bullets(slide, left, top, width, height, items, font_size=15):
        box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(10)
            r = p.add_run()
            r.text = f"•  {item}"
            r.font.name = "Montserrat"
            r.font.size = Pt(font_size)
            r.font.color.rgb = MUTED

    # Slide 1: Capa
    s1 = prs.slides.add_slide(blank)
    set_bg(s1)
    bar = s1.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.28), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = MAGENTA
    bar.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.0), Inches(3.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "RESPIRACIDADÃO"
    r.font.name = "Montserrat"
    r.font.size = Pt(46)
    r.font.bold = True
    r.font.color.rgb = MAGENTA

    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = "Classificação Preditiva de Risco Respiratório com Machine Learning"
    r2.font.name = "Montserrat"
    r2.font.size = Pt(24)
    r2.font.bold = True
    r2.font.color.rgb = WHITE

    p3 = tf.add_paragraph()
    p3.space_before = Pt(24)
    r3 = p3.add_run()
    r3.text = (
        "FIAP Global Solution 2026.2 | 06 Machine Learning & Modelling\n"
        "Sala: 1TIAPZ1  |  Grupo: Perceptron\n"
        "Giovanni Henrique Pereira Hessel (RM 570574)\n"
        "Suellen Pereira da Silva (RM 573862)\n"
        "Israel Carneiro de Toledo (RM 573854)"
    )
    r3.font.name = "Montserrat"
    r3.font.size = Pt(14)
    r3.font.color.rgb = MUTED

    # Slide 2: Problema, Publico, Base e Arquitetura
    s2 = prs.slides.add_slide(blank)
    set_bg(s2)
    add_header(s2, "1. Problema CitizenTech, Dados Reais e Arquitetura", "ODS 3 (Saúde e Bem-Estar) e ODS 11 (Cidades Sustentáveis)")
    add_bullets(s2, 0.7, 1.5, 5.7, 5.2, [
        "Problema: fumaça de queimadas e poluição urbana agravam crises de asma e DPOC.",
        "Público: crianças em escolas, idosos e pacientes respiratórios em periferias.",
        "Dataset real: UCI Air Quality (9.357 registros brutos, 6.941 leituras horárias completas).",
        "Alvo sem data leakage: risco respiratório derivado de CO(GT) (<1.5 Normal, 1.5 a 3.0 Atenção, >=3.0 Crítico), excluído das 11 variáveis de entrada.",
        "Pré-processamento: StandardScaler encapsulado em Pipeline scikit-learn, split estratificado 80/20.",
    ])
    s2.shapes.add_picture(str(ASSETS_DIR / "arquitetura_uml_respiracidadao.png"), Inches(6.6), Inches(1.55), width=Inches(6.1))

    # Slide 3: EDA
    s3 = prs.slides.add_slide(blank)
    set_bg(s3)
    add_header(s3, "2. Análise Exploratória de Dados (EDA)", "Proporção entre as 3 classes de risco respiratório")
    s3.shapes.add_picture(str(ROOT / "packages" / "ml-modelling" / "charts" / "01_eda_classes_box.png"), Inches(0.8), Inches(1.55), width=Inches(11.6))
    add_bullets(s3, 0.8, 5.95, 11.6, 1.2, [
        "Distribuição por classe: 2.531 Normal (36,5%), 2.718 Atenção (39,2%) e 1.692 Crítico (24,4%), com separação clara por concentração química (C6H6, PT08.S1, PT08.S2).",
    ], font_size=14)

    # Slide 4: Comparacao de Modelos e Tuning
    s4 = prs.slides.add_slide(blank)
    set_bg(s4)
    add_header(s4, "3. Comparação de Algoritmos e Otimização (CV=5)", "Baseline linear vs ensembles e tuning via RandomizedSearchCV")
    rows = ml["comparacao_modelos"]
    tbl_shape = s4.shapes.add_table(len(rows) + 1, 5, Inches(0.7), Inches(1.65), Inches(11.9), Inches(3.8))
    table = tbl_shape.table
    headers = ["Algoritmo", "Train Acc", "Test Acc", "Test F1-Macro", "Gap Overfit"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = MAGENTA
        cell.text = h
        cell.text_frame.paragraphs[0].font.size = Pt(13)
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.color.rgb = WHITE

    for r_idx, row in enumerate(rows, start=1):
        vals = [
            row["modelo"],
            f"{row['train_acc']*100:.2f}%",
            f"{row['test_acc']*100:.2f}%",
            f"{row['test_f1_macro']*100:.2f}%",
            f"{row['gap_overfit']*100:.2f}%",
        ]
        for c_idx, val in enumerate(vals):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD
            cell.text = val
            cell.text_frame.paragraphs[0].font.size = Pt(12)
            cell.text_frame.paragraphs[0].font.color.rgb = WHITE if c_idx == 0 else CYAN

    add_bullets(s4, 0.7, 5.7, 11.9, 1.3, [
        f"Modelo final escolhido: RandomForestClassifier Tuned (250 árvores, min_samples_leaf=2) com F1-Macro CV={ml['cv_f1_macro']:.4f} e Teste Accuracy={ml['teste_accuracy']*100:.2f}%.",
    ], font_size=14)

    # Slide 5: Matriz de Confusao & Feature Importance
    s5 = prs.slides.add_slide(blank)
    set_bg(s5)
    add_header(s5, "4. Matriz de Confusão e Importância das Variáveis", f"Apenas {ml['matriz_confusao'][0][2] + ml['matriz_confusao'][2][0]} confusão direta entre Normal e Crítico no conjunto de teste")
    s5.shapes.add_picture(str(ROOT / "packages" / "ml-modelling" / "charts" / "02_confusao_feature_importance.png"), Inches(0.75), Inches(1.5), width=Inches(11.8))

    # Slide 6: Demo em producao e Limitacoes
    s6 = prs.slides.add_slide(blank)
    set_bg(s6)
    add_header(s6, "5. Aplicação Real, Limitações e Próximos Passos", "Inferência em produção na API FastAPI (/predict) e App React")
    add_bullets(s6, 0.8, 1.6, 11.7, 5.2, [
        "Inferência validada em cenários não vistos: Manhã limpa (100% Normal), Tráfego intenso (98,5% Atenção), Queimada crítica (100% Crítico).",
        "Benefício direto: antecipa picos antes do agravamento respiratório e orienta escolas e UBS em tempo real.",
        "Limitações: dados calibrados no clima italiano (UCI) exigem recalibração com estações brasileiras (CETESB / INPE) para operação oficial.",
        "Evolução futura: acoplamento com séries temporais horárias e notificação push comunitária com acessibilidade em áudio.",
        "ODS 3 (Saúde e Bem-Estar), ODS 10 (Redução das Desigualdades) e ODS 11 (Cidades Sustentáveis).",
    ], font_size=16)

    out_pptx = DOCS_DIR / "06_RespiraCidadao_ML_Slides.pptx"
    prs.save(str(out_pptx))
    print(f"Slides gerados em {out_pptx}")


if __name__ == "__main__":
    build_architecture_diagram()
    build_ml_slides()
