import { useState } from "react";
import { KeyRound, Lock, ShieldAlert, Zap } from "lucide-react";
import { api } from "../api";
import type { AuditResponse } from "../types";

interface SecurityTabProps {
  audit: AuditResponse | null;
  onRefresh: () => Promise<void>;
}

export function SecurityTab({ audit, onRefresh }: SecurityTabProps) {
  const [burstResult, setBurstResult] = useState<string | null>(null);
  const [xssResult, setXssResult] = useState<string | null>(null);
  const [keyInput, setKeyInput] = useState("");
  const [authResult, setAuthResult] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const testXssSanitization = async () => {
    setBusy(true);
    try {
      const res = await api.createOcorrenciaRaw({
        dispositivo_id: "esp32-sec-test",
        tipo: "esp32",
        metrica: "fumaca_ppm",
        valor: 92.0,
        relato: "<script>alert('xss')</script> Fumaça leve na praça",
      });
      setXssResult(`HTTP ${res.status}: relato salvo sanitizado = ${JSON.stringify((res.body as { relato?: string }).relato ?? res.body)}`);
      await onRefresh();
    } catch (e) {
      setXssResult(`Falha ao chamar a API: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  };

  const testAuthKey = async (useKey: boolean) => {
    if (
      useKey &&
      keyInput &&
      !window.confirm("Com uma chave válida este teste APAGA todas as ocorrências registradas. Continuar?")
    ) {
      return;
    }
    setBusy(true);
    try {
      const res = await api.testClearWithKey(useKey ? keyInput : undefined);
      setAuthResult(`DELETE /ocorrencias -> HTTP ${res.status}: ${JSON.stringify(res.body)}`);
      await onRefresh();
    } catch (e) {
      setAuthResult(`Falha ao chamar a API: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  };

  const testRateBurst = async () => {
    setBusy(true);
    setBurstResult("Disparando rajada de requisições para testar janela deslizante HTTP 429...");
    try {
      const limit = audit?.rate_limit.max_requests ?? 30;
      const calls = Math.min(limit + 3, 35);
      let okCount = 0;
      let blockedCount = 0;
      for (let i = 0; i < calls; i++) {
        const res = await api.createOcorrenciaRaw({
          dispositivo_id: "esp32-burst-ui",
          tipo: "esp32",
          metrica: "fumaca_ppm",
          valor: 50 + i,
          relato: "Teste controlado de rate limit",
        });
        if (res.status === 201) okCount++;
        else if (res.status === 429) {
          blockedCount++;
          break;
        }
      }
      setBurstResult(`Resultado da rajada: ${okCount} aceitas (201), ${blockedCount} bloqueada(s) por Rate Limit (HTTP 429).`);
      await onRefresh();
    } catch (e) {
      setBurstResult(`Falha ao chamar a API: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div className="grid-2">
        <div className="card card-accent">
          <div className="section-header">
            <h2 className="section-title">
              <ShieldAlert size={18} color="#ed145b" /> Demonstração ao Vivo de Controles (03 Cybersecurity)
            </h2>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button className="btn btn-sm" disabled={busy} onClick={testXssSanitization}>
                <Lock size={14} /> Testar Sanitização XSS
              </button>
              <button className="btn btn-danger btn-sm" disabled={busy} onClick={testRateBurst}>
                <Zap size={14} /> Testar Rate Limiting (429)
              </button>
            </div>
            {xssResult && <div className="alert-banner ok">{xssResult}</div>}
            {burstResult && <div className="alert-banner crit">{burstResult}</div>}

            <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 12 }}>
              <label htmlFor="sec-api-key" style={{ fontSize: "0.78rem", color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                Teste de Autenticação Administrativa (X-API-Key em DELETE /ocorrencias)
              </label>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <input
                  id="sec-api-key"
                  aria-label="Chave administrativa RESPIRA_API_KEY"
                  autoComplete="off"
                  type="password"
                  placeholder="Informe RESPIRA_API_KEY"
                  value={keyInput}
                  onChange={(e) => setKeyInput(e.target.value)}
                  style={{ flex: 1, minWidth: 180 }}
                />
                <button className="btn btn-sm" disabled={busy} onClick={() => testAuthKey(false)}>
                  Testar Sem Chave (401)
                </button>
                <button className="btn btn-primary btn-sm" disabled={busy} onClick={() => testAuthKey(true)}>
                  <KeyRound size={14} /> Testar Com Chave
                </button>
              </div>
              {authResult && (
                <div className="alert-banner ok" style={{ marginTop: 10 }}>
                  {authResult}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="section-header">
            <h2 className="section-title">LGPD &amp; Superfície de Ataque (5 Camadas)</h2>
          </div>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: "0.83rem", color: "var(--text-secondary)", lineHeight: 1.7 }}>
            <li><strong>Dados coletados:</strong> telemetria ambiental anônima, coordenadas aproximadas de estação pública e relato textual opcional. Sem CPF, nome ou e-mail.</li>
            <li><strong>Camadas protegidas:</strong> Usuário (sem exposição de segredos), Aplicação (sanitização XSS/CSV), API (Sliding-Window Rate Limit {audit?.rate_limit.max_requests ?? 30} req/{audit?.rate_limit.window_sec ?? 60}s), Banco (SQL parametrizado + SHA-256) e Modelo IA (validação de faixa `PredictIn` + fallback determinístico).</li>
            <li><strong>Transparência:</strong> aviso claro ao cidadão no envio do relato recomendando não informar dados pessoais de saúde identificáveis.</li>
          </ul>
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <h2 className="section-title">Trilha de Auditoria de Segurança (JSONL)</h2>
          <span className="pill cyan">{audit?.events.length ?? 0} eventos recentes</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Timestamp (UTC)</th>
                <th>Evento</th>
                <th>Severidade</th>
                <th>IP</th>
                <th>Status</th>
                <th>Detalhe</th>
              </tr>
            </thead>
            <tbody>
              {(audit?.events ?? []).map((ev, idx) => (
                <tr key={`${ev.timestamp}-${idx}`}>
                  <td className="mono" style={{ fontSize: "0.74rem" }}>{ev.timestamp}</td>
                  <td className="mono">{ev.event}</td>
                  <td>
                    <span className={`pill ${ev.severity === "critical" ? "crit" : ev.severity === "warning" ? "warn" : "ok"}`}>
                      {ev.severity}
                    </span>
                  </td>
                  <td className="mono">{ev.client_ip}</td>
                  <td className="mono">{ev.status_code}</td>
                  <td>{ev.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
