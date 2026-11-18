#!/usr/bin/env python3
"""Transforma as saídas reais de terminal (docs/evidencias/*.txt) em prints PNG e desenha o diagrama UML de sequência."""

import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "docs" / "evidencias"
ASSETS = ROOT / "docs" / "assets"

TERM_BG, TERM_FG, TERM_CMD, TERM_NOTE = "#17201f", "#e8ece9", "#7fd1c7", "#9aa5a2"
BG, INK, MUTED, LINE, BRAND, CRITICO = "#f6f5f1", "#17201f", "#5b6664", "#c9c6bd", "#0f6b66", "#c8372d"


def terminal_png(txt: Path) -> Path:
    """Desenha o texto como um terminal: comandos em verde-água, comentários em cinza."""
    raw = txt.read_text(encoding="utf-8").rstrip("\n").split("\n")
    lines = []
    for l in raw:
        parts = textwrap.wrap(l, 100, subsequent_indent="    ", break_long_words=True, drop_whitespace=False) or [""]
        lines.extend(parts if len(l) > 100 else [l])
    width = max(len(l) for l in lines)
    fig_w = max(6.0, width * 0.075 + 0.6)
    fig_h = len(lines) * 0.19 + 0.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(TERM_BG)
    ax.set_facecolor(TERM_BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(lines) + 1)
    for i, line in enumerate(lines):
        color = TERM_CMD if line.startswith("$") else TERM_NOTE if line.startswith("#") else TERM_FG
        ax.text(0.01, len(lines) - i, line, family="DejaVu Sans Mono", fontsize=9, color=color, va="center")
    out = EVID / f"{txt.stem}.png"
    fig.savefig(out, dpi=170, bbox_inches="tight", facecolor=TERM_BG, pad_inches=0.15)
    plt.close(fig)
    return out


def sequence_diagram() -> Path:
    """UML de sequência: o caminho de uma leitura de ar ruim, do sensor ao app."""
    actors = ["Sensor ESP32", "Central (API)", "Modelo", "Banco + CSV", "App"]
    xs = [1, 3.2, 5.4, 7.6, 9.8]
    msgs = [
        (0, 0, "mede gases, CO, T, UR; acende LED vermelho e buzzer", False),
        (0, 1, "POST /ocorrencias {JSON}", False),
        (1, 1, "valida (Pydantic) e aplica limiares", False),
        (1, 2, "field_risk(4 medidas)", False),
        (2, 1, "crítico, 93%", True),
        (1, 3, "grava leitura + selo HMAC", False),
        (1, 0, "201 Created", True),
        (4, 1, "GET /locais", False),
        (1, 4, "nível, frase, o que fazer", True),
    ]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    top, bottom = 10.4, 0.3
    ax.set_xlim(0, 10.8)
    ax.set_ylim(bottom - 0.2, top + 0.9)
    for name, x in zip(actors, xs):
        ax.add_patch(plt.Rectangle((x - 0.85, top), 1.7, 0.65, facecolor="white", edgecolor=INK, lw=1.2))
        ax.text(x, top + 0.33, name, ha="center", va="center", fontsize=9.5, color=INK, weight="bold")
        ax.plot([x, x], [bottom, top], ls=(0, (4, 3)), color=LINE, lw=1)
    y = top - 0.7
    for a, b, label, ret in msgs:
        if a == b:
            x = xs[a]
            ax.annotate("", xy=(x + 0.05, y - 0.35), xytext=(x + 0.05, y),
                        arrowprops=dict(arrowstyle="-|>", color=BRAND, lw=1.2, connectionstyle="arc3,rad=-1.4"))
            ax.text(x + 0.45, y - 0.15, label, fontsize=8.5, color=INK, va="center")
            y -= 1.05
            continue
        ax.annotate("", xy=(xs[b], y), xytext=(xs[a], y),
                    arrowprops=dict(arrowstyle="-|>", color=MUTED if ret else BRAND, lw=1.2, ls="--" if ret else "-"))
        ax.text((xs[a] + xs[b]) / 2, y + 0.17, label, ha="center", fontsize=8.5, color=CRITICO if "93%" in label else INK)
        y -= 1.05
    ax.text(0.1, top + 0.82, "Diagrama de sequência (UML): leitura de ar ruim na escola", fontsize=11, color=INK, weight="bold")
    out = ASSETS / "uml_sequencia_leitura.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    return out


if __name__ == "__main__":
    for txt in sorted(EVID.glob("*.txt")):
        print("print:", terminal_png(txt).name)
    print("uml:", sequence_diagram().name)
