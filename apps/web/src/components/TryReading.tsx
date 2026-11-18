import { useEffect, useState } from "react";
import { api } from "../api";
import type { Level, PredictResult } from "../types";
import { LEVEL_NAME, pct } from "../format";

const FIELDS = [
  { key: "gas_voc", label: "Fumaça e gases", min: 400, max: 1800, step: 10, unit: "" },
  { key: "gas_co", label: "Monóxido de carbono", min: 650, max: 1800, step: 10, unit: "" },
  { key: "temperatura_c", label: "Temperatura", min: 0, max: 40, step: 1, unit: " °C" },
  { key: "umidade_pct", label: "Umidade do ar", min: 10, max: 90, step: 1, unit: "%" },
] as const;

type Values = Record<(typeof FIELDS)[number]["key"], number>;

const PRESETS: { name: string; v: Values }[] = [
  { name: "Manhã limpa", v: { gas_voc: 706, gas_co: 925, temperatura_c: 18, umidade_pct: 55 } },
  { name: "Trânsito parado", v: { gas_voc: 980, gas_co: 1120, temperatura_c: 24, umidade_pct: 42 } },
  { name: "Queimada perto", v: { gas_voc: 1280, gas_co: 1383, temperatura_c: 31, umidade_pct: 34 } },
];

export function TryReading() {
  const [v, setV] = useState<Values>(PRESETS[1].v);
  const [res, setRes] = useState<PredictResult | null>(null);

  useEffect(() => {
    const t = setTimeout(() => api.predict(v).then(setRes).catch(() => setRes(null)), 250);
    return () => clearTimeout(t);
  }, [v]);

  const answers: [string, Level | undefined, number | undefined][] = res
    ? [
        ["Luz do sensor", res.regra_local.classe, undefined],
        ["Central", res.ml?.classe, res.ml ? res.ml.probabilidades[res.ml.classe] : undefined],
        ["Segunda opinião", res.nn?.classe, res.nn ? res.nn.probabilidades[res.nn.classe] : undefined],
      ]
    : [];

  return (
    <section className="card try">
      <h3>Teste uma leitura</h3>
      <p className="muted">Mexa nos valores e veja o que a luz e a central respondem. Os números de gás são o índice cru do sensor.</p>
      <div className="presets">
        {PRESETS.map((p) => (
          <button key={p.name} className="chip" onClick={() => setV(p.v)}>{p.name}</button>
        ))}
      </div>
      <div className="try-grid">
        <div>
          {FIELDS.map((f) => (
            <label key={f.key} className="slider">
              <span>{f.label}<b>{v[f.key]}{f.unit}</b></span>
              <input type="range" min={f.min} max={f.max} step={f.step} value={v[f.key]} onChange={(e) => setV({ ...v, [f.key]: Number(e.target.value) })} />
            </label>
          ))}
        </div>
        <ul className="answers" aria-live="polite">
          {answers.map(([who, lvl, p]) => (
            <li key={who} className={lvl}>
              <small>{who}</small>
              <strong>{lvl ? LEVEL_NAME[lvl] : "indisponível"}</strong>
              {p != null && <small>{pct(p)} de confiança</small>}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
