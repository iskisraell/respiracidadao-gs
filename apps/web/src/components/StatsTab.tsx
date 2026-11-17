import { BarChart3 } from "lucide-react";
import type { StatsSummaryResponse } from "../types";

export function StatsTab({ summary }: { summary: StatsSummaryResponse | null }) {
  const est = summary?.estatistica;
  if (!est) {
    return (
      <div className="card">
        <p style={{ color: "var(--text-dim)" }}>Resumo estatístico não encontrado.</p>
      </div>
    );
  }

  const { item_02_normal: norm, item_03_testes_hipotese: hyp, item_04_regressao_simples: regS, item_05_regressao_multipla: regM, item_06_regressao_logistica: logi } = est;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div className="kpi-grid">
        <div className="card card-accent">
          <p className="kpi-label">Base Real Auditada</p>
          <p className="kpi-value tabular">{est.dataset.registros_limpos.toLocaleString("pt-BR")}</p>
          <p className="kpi-sub">de {est.dataset.registros_brutos.toLocaleString("pt-BR")} leituras UCI Air Quality</p>
        </div>
        <div className="card">
          <p className="kpi-label">Regressão Simples (R²)</p>
          <p className="kpi-value tabular" style={{ color: "var(--color-cyan)" }}>
            {(regS.r2 * 100).toFixed(2)}%
          </p>
          <p className="kpi-sub">Pearson r = {regS.pearson_r} | F = {regS.teste_f}</p>
        </div>
        <div className="card">
          <p className="kpi-label">Regressão Múltipla (R²)</p>
          <p className="kpi-value tabular" style={{ color: "var(--color-ok)" }}>
            {(regM.r2 * 100).toFixed(2)}%
          </p>
          <p className="kpi-sub">R² ajustado = {regM.r2_ajustado} | F = {regM.teste_f}</p>
        </div>
        <div className="card">
          <p className="kpi-label">Logística Binária (Acc)</p>
          <p className="kpi-value tabular" style={{ color: "var(--color-magenta-light)" }}>
            {(logi.acuracia_teste * 100).toFixed(2)}%
          </p>
          <p className="kpi-sub">F1 Crítico = {(logi.f1_critico * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="section-header">
            <h2 className="section-title">
              <BarChart3 size={18} color="#ed145b" /> 02. Probabilidade Normal: {norm.variavel}
            </h2>
          </div>
          <p style={{ fontSize: "0.84rem", color: "var(--text-secondary)", marginTop: 0 }}>
            Média = <strong className="mono">{norm.media}</strong> mg/m³, Desvio padrão ={" "}
            <strong className="mono">{norm.desvio_padrao}</strong>, Mediana ={" "}
            <strong className="mono">{norm.mediana}</strong>.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Cálculo</th>
                  <th>Probabilidade</th>
                  <th>Classificação</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="mono">P(X &lt; média)</td>
                  <td className="mono">{(norm.p_menor_media * 100).toFixed(2)}%</td>
                  <td>{norm.classificacao_a}</td>
                </tr>
                <tr>
                  <td className="mono">P(X &gt; mediana)</td>
                  <td className="mono">{(norm.p_maior_mediana * 100).toFixed(2)}%</td>
                  <td>{norm.classificacao_b}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <div className="section-header">
            <h2 className="section-title">03. Testes de Hipótese para a Média (Z-Test)</h2>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Hipótese H1</th>
                  <th>n / α</th>
                  <th>Z calc vs crit</th>
                  <th>p-valor</th>
                  <th>Decisão</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="mono">μ &lt; μ_pop</td>
                  <td className="mono">n=20 / 6%</td>
                  <td className="mono">
                    {hyp.teste_3a_unilateral_esquerda.z_calculado} / {hyp.teste_3a_unilateral_esquerda.z_critico}
                  </td>
                  <td className="mono">{hyp.teste_3a_unilateral_esquerda.p_valor}</td>
                  <td>{hyp.teste_3a_unilateral_esquerda.decisao}</td>
                </tr>
                <tr>
                  <td className="mono">μ &gt; μ_pop</td>
                  <td className="mono">n=25 / 9%</td>
                  <td className="mono">
                    {hyp.teste_3b_unilateral_direita.z_calculado} / {hyp.teste_3b_unilateral_direita.z_critico}
                  </td>
                  <td className="mono">{hyp.teste_3b_unilateral_direita.p_valor}</td>
                  <td>{hyp.teste_3b_unilateral_direita.decisao}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <h2 className="section-title">04 a 06. Equações Estatísticas Ajustadas</h2>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: "0.84rem" }}>
          <div>
            <strong>Regressão Linear Simples:</strong>{" "}
            <code style={{ color: "var(--color-cyan)" }}>{regS.equacao}</code>
          </div>
          <div>
            <strong>Regressão Linear Múltipla:</strong>{" "}
            <code style={{ color: "var(--color-ok)" }}>{regM.equacao}</code>
          </div>
          <div>
            <strong>Regressão Logística Binária:</strong>{" "}
            <code style={{ color: "var(--color-magenta-light)" }}>{logi.equacao_logit}</code>
          </div>
        </div>
      </div>
    </div>
  );
}
