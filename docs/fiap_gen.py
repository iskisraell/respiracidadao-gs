#!/usr/bin/env python3
"""Roda o gerador fiap-doc com uma correção: a figura não empurra a legenda para a página seguinte.

No fpdf2, image() já avança o cursor pela altura da figura; o gerador original avançava de novo,
deixando um vão do tamanho da figura antes da legenda. Uso: fiap_gen.py <gerador.py> <conteudo.json>
"""

import importlib.util
import os
import sys

spec = importlib.util.spec_from_file_location("fiap_generate", sys.argv[1])
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def _image(self, path, caption=None, max_w=None):
    p = self.pdf
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    from PIL import Image

    px_w, px_h = Image.open(path).size
    w = max_w or gen.CONTENT_W
    h = w * px_h / px_w
    if h > 180:
        h = 180
        w = h * px_w / px_h
    needed = h + (12 if caption else 4)
    if p.get_y() + needed > 270:
        p.add_page()
    y = p.get_y()
    p.image(path, x=gen.MARGIN_L + (gen.CONTENT_W - w) / 2, y=y, w=w, h=h)
    p.set_y(y + h + 2)
    if caption:
        p.set_font("Montserrat", "I", 8)
        p.set_text_color(*gen.MID_GRAY)
        p.multi_cell(0, 4.5, caption, align="C")
    p.ln(4)


gen.FIAPPDF._image = _image
sys.argv = [sys.argv[1]] + sys.argv[2:]
gen.main()
