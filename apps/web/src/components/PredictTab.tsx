import { useState } from "react";
import { Brain, Cpu, Sparkles } from "lucide-react";
import { api } from "../api";
import type { ModelVerdict, PredictInput, PredictResponse, RiskLevel, StatsSummaryResponse } from "../types";

interface PredictTabProps {
  summary: StatsSummaryResponse | null;
}

const PRESETS: Record<string, { label: string; data: PredictInput }> = {
  normal: {
    label: "Manhã Limpa (Normal)",
    data: {
      co_sensor_s1: 890,
      c6h6_gt: 4.2,
      nmhc_sensor_s2: 720,
      nox_gt: 75,
      nox_sensor_s3: 1080,
      no2_gt: 68,
      no2_sensor_s4: 1280,
      o3_sensor_s5: 640,
      temperatura_c: 21.0,
      umidade_pct: 58.0,
      umidade_absoluta: 1.42,
    },
  },
  atencao: {
    label: "Tráfego Intenso (Atenção)",
    data: {
      co_sensor_s1: 1160,
      c6h6_gt: 10.8,
      nmhc_sensor_s2: 995,
      nox_gt: 210,
      nox_sensor_s3: 780,
      no2_gt: 118,
      no2_sensor_s4: 1520,
      o3_sensor_s5: 1040,
      temperatura_c: 25.5,
      umidade_pct: 42.0,
      umidade_absoluta: 1.35,
    },
  },
  critico: {
    label: "Queimada Urbana (Crítico)",
    data: {
      co_sensor_s1: 1560,
      c6h6_gt: 24.5,
      nmhc_sensor_s2: 1410,
      nox_gt: 460,
      nox_sensor_s3: 510,
      no2_gt: 190,
      no2_sensor_s4: 1980,
      o3_sensor_s5: 1650,
      temperatura_c: 32.0,
      umidade_pct: 24.0,
      umidade_absoluta: 1.12,
    },
  },
};

const FIELDS: { key: keyof PredictInput; label: string; step?: number; min: number; max: number }[] = [
  { key: "co_sensor_s1", label: "PT08.S1 (CO)", min: 200, max: 3000 },
  { key: "c6h6_gt", label: "C6H6(GT) [µg/m³]", step: 0.1, min: 0.1, max: 80 },
  { key: "nmhc_sensor_s2", label: "PT08.S2 (NMHC)", min: 200, max: 3000 },
  { key: "nox_gt", label: "NOx(GT) [ppb]", min: 1, max: 2000 },
  { key: "nox_sensor_s3", label: "PT08.S3 (NOx)", min: 100, max: 3000 },
  { key: "no2_gt", label: "NO2(GT) [µg/m³]", min: 1, max: 500 },
  { key: "no2_sensor_s4", label: "PT08.S4 (NO2)", min: 200, max: 3500 },
  { key: "o3_sensor_s5", label: "PT08.S5 (O3)", min: 200, max: 3500 },
  { key: "temperatura_c", label: "Temperatura (°C)", step: 0.1, min: -10, max: 55 },
  { key: "umidade_pct", label: "Umidade Relativa (%)", step: 0.1, min: 5, max: 100 },
  { key: "umidade_absoluta", label: "Umidade Absoluta (AH)", step: 0.01, min: 0.1, max: 3.5 },
];

const RISK_TEXT: Record<RiskLevel, string> = {
  normal: "NORMAL",
  atencao: "ATENÇÃO",
  critico: "CRÍTICO",
};

const COLOR_MAP: Record<RiskLevel, string> = {
  normal: "var(--color-ok)",
  atencao: "var(--color-warn)",
  critico: "var(--color-crit)",
};

function VerdictCard({ title, verdict }: { title: string; verdict?: ModelVerdict }) {
  if (!verdict) {
    return (
      <div className="card">
        <p className="kpi-label">{title}</p>
        <p style={{ color: "var(--text-dim)", fontSize: "0.85rem" }}>
          Artefato ainda não carregado. Execute os notebooks para habilitar inferência.
        </p>
      </div>
    );
  }
  const pillCls = verdict.classe === "normal" ? "ok" : verdict.classe === "atencao" ? "warn" : "crit";
  return (
    <div className="card card-accent">
      <div className="section-header" style={{ marginBottom: 10 }}>
        <div>
          <p className="kpi-label" style={{ marginBottom: 2 }}>{title}</p>
          <div className="mono" style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
            {verdict.modelo}
          </div>
        </div>
        <span className={`pill ${pillCls}`} style={{ fontSize: "0.82rem", padding: "5px 12px" }}>
          {RISK_TEXT[verdict.classe]}
        </span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {(["normal", "atencao", "critico"] as RiskLevel[]).map((cls) => {
          const pct = Math.round((verdict.probabilidades[cls] ?? 0) * 1000) / 10;
          return (
            <div key={cls}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: 4 }}>
                <span style={{ fontWeight: 600 }}>{RISK_TEXT[cls]}</span>
                <span className="mono">{pct.toFixed(1)}%</span>
              </div>
              <div className="bar-track" role="progressbar" aria-label={`Probabilidade ${RISK_TEXT[cls]}`} aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
                <div className="bar-fill" style={{ width: `${pct}%`, background: COLOR_MAP[cls] }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function PredictTab({ summary }: PredictTabProps) {
  const [form, setForm] = useState<PredictInput>(PRESETS.atencao.data);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runPredict = async (payload: PredictInput) => {
    setBusy(true);
    setError(null);
    try {
      const res = await api.predict(payload);
      setResult(res);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const applyPreset = (key: string) => {
    const data = PRESETS[key].data;
    setForm(data);
    void runPredict(data);
  };

  const updateNum = (field: keyof PredictInput, value: string) => {
    setForm((prev) => ({ ...prev, [field]: Number(value) }));
  };

  const ml = summary?.machine_learning;
  const nn = summary?.redes_neurais;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div className="card">
        <div className="section-header">
          <h2 className="section-title">
            <Brain size={18} color="#ed145b" /> Simulador de Inferência Simultânea (Random Forest + PyTorch MLP)
          </h2>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {Object.entries(PRESETS).map(([k, p]) => (
              <button key={k} type="button" className="btn btn-sm" disabled={busy} onClick={() => applyPreset(k)}>
                {p.label}
              </button>
            ))}
            <button type="button" className="btn btn-primary btn-sm" disabled={busy} onClick={() => runPredict(form)}>
              <Sparkles size={14} aria-hidden="true" /> {busy ? "Executando..." : "Executar /predict"}
            </button>
          </div>
        </div>

        <div className="form-grid">
          {FIELDS.map((f) => (
            <div className="field" key={f.key}>
              <label htmlFor={`pred-${f.key}`}>{f.label}</label>
              <input
                id={`pred-${f.key}`}
                type="number"
                step={f.step ?? 1}
                min={f.min}
                max={f.max}
                value={form[f.key]}
                onChange={(e) => updateNum(f.key, e.target.value)}
              />
            </div>
          ))}
        </div>

        {error && (
          <div className="alert-banner crit" role="alert" style={{ marginTop: 12 }}>
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="grid-2">
          <VerdictCard title="06 Machine Learning (Scikit-Learn)" verdict={result.ml} />
          <VerdictCard title="08 Deep Learning (PyTorch)" verdict={result.nn} />
        </div>
      )}

      <div className="grid-2">
        <div className="card">
          <div className="section-header">
            <h2 className="section-title">
              <Cpu size={18} color="#64d2ff" /> Comparativo de Algoritmos (06 ML)
            </h2>
            {ml && <span className="pill ok">Teste Acc {(ml.teste_accuracy * 100).toFixed(2)}%</span>}
          </div>
          {ml ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Modelo</th>
                    <th>Train Acc</th>
                    <th>Test Acc</th>
                    <th>F1 Macro</th>
                    <th>Gap Overfit</th>
                  </tr>
                </thead>
                <tbody>
                  {ml.comparacao_modelos.map((row) => (
                    <tr key={row.modelo}>
                      <td style={{ fontWeight: 600 }}>{row.modelo}</td>
                      <td className="mono">{(row.train_acc * 100).toFixed(2)}%</td>
                      <td className="mono">{(row.test_acc * 100).toFixed(2)}%</td>
                      <td className="mono">{(row.test_f1_macro * 100).toFixed(2)}%</td>
                      <td className="mono">{(row.gap_overfit * 100).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: "var(--text-dim)" }}>Métricas de ML disponíveis após execução do notebook.</p>
          )}
        </div>

        <div className="card">
          <div className="section-header">
            <h2 className="section-title">Baseline vs Regularized MLP (08 Deep Learning)</h2>
            {nn && <span className="pill ok">Teste Acc {(nn.teste_accuracy * 100).toFixed(2)}%</span>}
          </div>
          {nn ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Experimento</th>
                      <th>Épocas</th>
                      <th>Train Acc</th>
                      <th>Test Acc</th>
                      <th>Gap</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nn.comparacao_experimentos.map((row) => (
                      <tr key={row.configuracao}>
                        <td style={{ fontWeight: 600 }}>{row.configuracao}</td>
                        <td className="mono">{row.epocas_executadas}</td>
                        <td className="mono">{(row.train_acc * 100).toFixed(2)}%</td>
                        <td className="mono">{(row.test_acc * 100).toFixed(2)}%</td>
                        <td className="mono">{(row.gap_overfit * 100).toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {ml && (
                <div>
                  <p className="kpi-label" style={{ marginBottom: 8 }}>Top 5 Variáveis Mais Importantes (Random Forest)</p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {ml.feature_importance.slice(0, 5).map((fi) => (
                      <div key={fi.feature}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem" }}>
                          <span className="mono">{fi.feature}</span>
                          <span className="mono">{(fi.importance * 100).toFixed(1)}%</span>
                        </div>
                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{ width: `${Math.min(100, fi.importance * 260)}%`, background: "var(--color-cyan)" }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: "var(--text-dim)" }}>Métricas da Rede Neural disponíveis após execução do notebook.</p>
          )}
        </div>
      </div>
    </div>
  );
}
