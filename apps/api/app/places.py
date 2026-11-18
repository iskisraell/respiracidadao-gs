"""Lugares monitorados, o que cada nível significa para quem está lá e o padrão de risco por hora."""

import csv
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

PLACES: List[Dict[str, object]] = [
    {
        "id": "escola-jardim-primavera",
        "nome": "Escola Jardim Primavera",
        "tipo": "escola",
        "bairro": "Zona Norte",
        "dispositivo_id": "esp32-escola-zona-norte",
        "latitude": -23.4892,
        "longitude": -46.6208,
    },
    {
        "id": "ubs-vila-esperanca",
        "nome": "UBS Vila Esperança",
        "tipo": "ubs",
        "bairro": "Vila Maria",
        "dispositivo_id": "esp32-ubs-vila-maria",
        "latitude": -23.5122,
        "longitude": -46.5917,
    },
    {
        "id": "praca-da-se",
        "nome": "Praça da Sé",
        "tipo": "praca",
        "bairro": "Centro",
        "dispositivo_id": "esp32-centro-01",
        "latitude": -23.5505,
        "longitude": -46.6333,
    },
]

PLACE_BY_ID = {p["id"]: p for p in PLACES}
PLACE_BY_DEVICE = {p["dispositivo_id"]: p for p in PLACES}

# O que dizer e o que fazer em cada nível. Mesmo texto no app, no alerta e nos documentos.
GUIDANCE: Dict[str, Dict[str, object]] = {
    "normal": {
        "titulo": "Ar bom agora",
        "frase": "Pode abrir as janelas e fazer atividades ao ar livre.",
        "acoes": ["Atividades ao ar livre liberadas", "Janelas abertas ajudam a ventilar"],
    },
    "atencao": {
        "titulo": "Ar carregado agora",
        "frase": "Quem tem asma, crianças pequenas e idosos devem evitar esforço ao ar livre.",
        "acoes": [
            "Troque a educação física por atividade em sala",
            "Deixe a bombinha de quem tem asma por perto",
            "Feche as janelas do lado da rua",
        ],
    },
    "critico": {
        "titulo": "Ar ruim agora",
        "frase": "Fique em ambiente fechado e avise quem tem problema respiratório.",
        "acoes": [
            "Cancele atividades ao ar livre",
            "Feche portas e janelas",
            "Avise famílias e pacientes com asma ou DPOC",
            "Falta de ar forte: procure a UBS ou ligue 192",
        ],
    },
}


@lru_cache(maxsize=1)
def hourly_pattern(csv_path: Path) -> List[Dict[str, float]]:
    """Fração de horas em cada nível, por hora do dia, na base real de 6.941 horas."""
    counts = [{"normal": 0, "atencao": 0, "critico": 0} for _ in range(24)]
    with csv_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            counts[int(row["Time"][:2])][row["nivel_risco"]] += 1
    pattern = []
    for hora, c in enumerate(counts):
        total = sum(c.values()) or 1
        pattern.append({"hora": hora, **{k: round(v / total, 3) for k, v in c.items()}})
    return pattern


def best_window(pattern: List[Dict[str, float]], start: int = 7, end: int = 18, size: int = 3) -> Dict[str, object]:
    """Janela de `size` horas, dentro do horário de aula, com menor risco crítico médio."""
    best = None
    for h in range(start, end - size + 1):
        media = sum(pattern[i]["critico"] for i in range(h, h + size)) / size
        if best is None or media < best["critico_medio"]:
            best = {"inicio": h, "fim": h + size, "critico_medio": round(media, 3)}
    pior = max(pattern[start:end], key=lambda p: p["critico"])
    return {**best, "pior_hora": pior["hora"], "pior_critico": pior["critico"]}
