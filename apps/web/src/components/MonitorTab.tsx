import { useState } from "react";
import { Activity, Cpu, Play, RefreshCw, Send, ShieldCheck } from "lucide-react";
import { api } from "../api";
import type { DeviceType, Indicators, Occurrence, RiskLevel } from "../types";

interface MonitorTabProps {
  occurrences: Occurrence[];
  indicators: Indicators | null;
  onRefresh: () => Promise<void>;
}

const RISK_LABEL: Record<RiskLevel, { text: string; cls: string }> = {
  normal: { text: "NORMAL", cls: "ok" },
  atencao: { text: "ATENÇÃO", cls: "warn" },
  critico: { text: "CRÍTICO", cls: "crit" },
};

export function MonitorTab({ occurrences, indicators, onRefresh }: MonitorTabProps) {
  const [filterRisk, setFilterRisk] = useState<string>("todos");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "ok" | "crit"; msg: string } | null>(null);
  const [verifyMsg, setVerifyMsg] = useState<string | null>(null);

  const [deviceId, setDeviceId] = useState("esp32-respira-01");
  const [tipo, setTipo] = useState<DeviceType>("esp32");
  const [metrica, setMetrica] = useState("fumaca_ppm");
  const [valor, setValor] = useState("275.0");
  const [temp, setTemp] = useState("33.4");
  const [umid, setUmid] = useState("26.0");
  const [relato, setRelato] = useState("Fumaça intensa próxima à escola municipal");

  const visible =
    filterRisk === "todos"
      ? occurrences
      : occurrences.filter((o) => o.nivel_risco === filterRisk);

  const runSimulation = async (cenario: "todos" | RiskLevel) => {
    setBusy(true);
    setFeedback(null);
    try {
      const res = await api.simulate(cenario, "esp32");
      await onRefresh();
      setFeedback({
        type: "ok",
        msg: `${res.executados} ocorrência(s) IoT simuladas e gravadas em SQLite + CSV.`,
      });
    } catch (e) {
      setFeedback({ type: "crit", msg: (e as Error).message });
    } finally {
      setBusy(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setFeedback(null);
    try {
      const res = await api.createOcorrenciaRaw({
        dispositivo_id: deviceId,
        tipo,
        metrica,
        valor: Number(valor),
        temperatura_c: temp.trim() === "" ? undefined : Number(temp),
        umidade_pct: umid.trim() === "" ? undefined : Number(umid),
        relato,
      });
      if (res.status === 201) {
        await onRefresh();
        const r = res.body as Occurrence;
        setFeedback({
          type: "ok",
          msg: `Leitura #${r.id} gravada. Classificação: ${r.nivel_risco.toUpperCase()} | Sentimento: ${r.ia_sentimento}.`,
        });
      } else {
        setFeedback({
          type: "crit",
          msg: `HTTP ${res.status}: ${JSON.stringify(res.body)}`,
        });
      }
    } catch (err) {
      setFeedback({ type: "crit", msg: (err as Error).message });
    } finally {
      setBusy(false);
    }
  };

  const handleVerify = async (id: number) => {
    try {
      const res = await api.verifyIntegrity(id);
      setVerifyMsg(
        `Registro #${res.id}: ${res.integro ? "SHA-256 íntegro" : "HASH DIVERGENTE"} (${res.hash_recalculado.slice(0, 16)}...)`
      );
    } catch (err) {
      setVerifyMsg((err as Error).message);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div className="kpi-grid">
        <div className="card card-accent">
          <p className="kpi-label">Leituras Persistidas</p>
          <p className="kpi-value tabular">{indicators?.total_leituras ?? 0}</p>
          <p className="kpi-sub">SQLite + CSV sincronizados</p>
        </div>
        <div className="card">
          <p className="kpi-label">Alertas Disparados</p>
          <p className="kpi-value tabular" style={{ color: "var(--color-warn)" }}>
            {indicators?.total_alertas ?? 0}{" "}
            <span style={{ fontSize: "0.95rem", color: "var(--text-secondary)" }}>
              ({indicators?.pct_alertas ?? 0}%)
            </span>
          </p>
          <p className="kpi-sub">
            Críticos: {indicators?.por_risco?.critico ?? 0} | Atenção: {indicators?.por_risco?.atencao ?? 0}
          </p>
        </div>
        <div className="card">
          <p className="kpi-label">Média de Concentração</p>
          <p className="kpi-value tabular" style={{ color: "var(--color-cyan)" }}>
            {indicators?.media_valor ?? 0}
          </p>
          <p className="kpi-sub">Unidade ativa: fumaca_ppm / sensores</p>
        </div>
        <div className="card">
          <p className="kpi-label">Pico Registrado</p>
          <p className="kpi-value tabular" style={{ color: "var(--color-magenta-light)" }}>
            {indicators?.max_valor ?? 0}
          </p>
          <p className="kpi-sub">Limiar crítico fumaça: &gt;= 250 ppm</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="section-header">
            <h2 className="section-title">
              <Cpu size={18} color="#ed145b" /> Simulador IoT &amp; Envio Manual
            </h2>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button
                className="btn btn-primary btn-sm"
                disabled={busy}
                onClick={() => runSimulation("todos")}
              >
                <Play size={14} /> Simular 3 Cenários
              </button>
              <button className="btn btn-sm" disabled={busy} onClick={onRefresh}>
                <RefreshCw size={14} /> Atualizar
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="dev-id">Dispositivo ID</label>
                <input id="dev-id" value={deviceId} onChange={(e) => setDeviceId(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="dev-tipo">Tipo</label>
                <select id="dev-tipo" value={tipo} onChange={(e) => setTipo(e.target.value as DeviceType)}>
                  <option value="esp32">ESP32 (Wokwi)</option>
                  <option value="drone">Drone</option>
                  <option value="app">App Cidadão</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="dev-metrica">Métrica</label>
                <select id="dev-metrica" value={metrica} onChange={(e) => setMetrica(e.target.value)}>
                  <option value="fumaca_ppm">fumaca_ppm (120 / 250)</option>
                  <option value="co_mg_m3">co_mg_m3 (4.0 / 9.0)</option>
                  <option value="no2_ug_m3">no2_ug_m3 (100 / 200)</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="dev-valor">Valor Medido</label>
                <input
                  id="dev-valor"
                  type="number"
                  step="0.1"
                  value={valor}
                  onChange={(e) => setValor(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="dev-temp">Temp (°C)</label>
                <input id="dev-temp" type="number" step="0.1" value={temp} onChange={(e) => setTemp(e.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="dev-umid">Umidade (%)</label>
                <input id="dev-umid" type="number" step="0.1" value={umid} onChange={(e) => setUmid(e.target.value)} />
              </div>
            </div>

            <div className="field">
              <label htmlFor="dev-relato">Relato do Cidadão (analisado por NLP + sanitizado XSS)</label>
              <input id="dev-relato" value={relato} onChange={(e) => setRelato(e.target.value)} />
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: "0.76rem", color: "var(--text-dim)" }}>
                Contrato compartilhado: 02 AICSS, 05 Python e 07 Cloud Lambda
              </span>
              <button className="btn btn-primary" type="submit" disabled={busy}>
                <Send size={14} /> Enviar Leitura POST
              </button>
            </div>
          </form>

          {feedback && (
            <div className={`alert-banner ${feedback.type}`} role="status" style={{ marginTop: 12 }}>
              {feedback.msg}
            </div>
          )}
        </div>

        <div className="card">
          <div className="section-header">
            <h2 className="section-title">
              <Activity size={18} color="#64d2ff" /> Arquitetura de Hardware ESP32 (02 AICSS)
            </h2>
            <span className="pill cyan">Wokwi Ready</span>
          </div>
          <p style={{ fontSize: "0.84rem", color: "var(--text-secondary)", marginTop: 0 }}>
            O nó comunitário lê fumaça via ADC (<span className="mono">GPIO 34</span>) e temperatura/umidade via{" "}
            <span className="mono">DHT22 (GPIO 15)</span>, aciona LEDs e buzzer antes de enviar JSON ao servidor Python.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Faixa fumaça_ppm</th>
                  <th>Atuador Local</th>
                  <th>Classe API</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="mono">&lt; 120.0</td>
                  <td>LED Verde (GPIO 26) | Buzzer mudo</td>
                  <td>
                    <span className="pill ok">normal</span>
                  </td>
                </tr>
                <tr>
                  <td className="mono">120.0 .. 249.9</td>
                  <td>LED Amarelo (GPIO 27) | Pulso 180ms</td>
                  <td>
                    <span className="pill warn">atencao</span>
                  </td>
                </tr>
                <tr>
                  <td className="mono">&gt;= 250.0</td>
                  <td>LED Vermelho (GPIO 14) | Sirene 1800Hz</td>
                  <td>
                    <span className="pill crit">critico</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <h2 className="section-title">Feed de Telemetria em Tempo Real</h2>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {["todos", "normal", "atencao", "critico"].map((r) => (
              <button
                key={r}
                type="button"
                aria-pressed={filterRisk === r}
                className={`btn btn-sm ${filterRisk === r ? "btn-primary" : ""}`}
                onClick={() => setFilterRisk(r)}
              >
                {r === "todos" ? "TODOS" : RISK_LABEL[r as RiskLevel].text}
              </button>
            ))}
          </div>
        </div>

        {verifyMsg && (
          <div className="alert-banner ok" style={{ marginBottom: 12 }}>
            {verifyMsg}
          </div>
        )}

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Dispositivo</th>
                <th>Métrica / Valor</th>
                <th>Risco</th>
                <th>IA Sentimento</th>
                <th>Relato</th>
                <th>Integridade SHA-256</th>
              </tr>
            </thead>
            <tbody>
              {visible.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", color: "var(--text-dim)", padding: 24 }}>
                    Nenhuma ocorrência registrada ainda. Clique em "Simular 3 Cenários" acima.
                  </td>
                </tr>
              ) : (
                visible.slice(0, 25).map((item) => {
                  const badge = RISK_LABEL[item.nivel_risco];
                  return (
                    <tr key={item.id}>
                      <td className="mono">{item.id}</td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{item.dispositivo_id}</div>
                        <div className="mono" style={{ fontSize: "0.72rem", color: "var(--text-dim)" }}>
                          {item.tipo}
                        </div>
                      </td>
                      <td className="mono">
                        {item.metrica}: <strong>{item.valor}</strong>
                      </td>
                      <td>
                        <span className={`pill ${badge.cls}`}>{badge.text}</span>
                      </td>
                      <td>
                        <div className="mono" style={{ fontSize: "0.78rem" }}>
                          {item.ia_sentimento} {item.ia_confianca ? `(${(item.ia_confianca * 100).toFixed(0)}%)` : ""}
                        </div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>{item.ia_fonte}</div>
                      </td>
                      <td style={{ maxWidth: 280 }}>{item.relato || "Sem relato"}</td>
                      <td>
                        <button className="btn btn-sm" onClick={() => handleVerify(item.id)}>
                          <ShieldCheck size={13} />{" "}
                          <span className="mono">{item.hash_integridade.slice(0, 8)}</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
