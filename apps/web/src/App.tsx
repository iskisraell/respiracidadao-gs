import { useCallback, useEffect, useState } from "react";
import { Activity, BarChart3, Brain, Shield } from "lucide-react";
import { api } from "./api";
import { MonitorTab } from "./components/MonitorTab";
import { PredictTab } from "./components/PredictTab";
import { SecurityTab } from "./components/SecurityTab";
import { StatsTab } from "./components/StatsTab";
import type { AuditResponse, HealthResponse, Indicators, Occurrence, StatsSummaryResponse } from "./types";

type TabId = "monitor" | "predict" | "stats" | "security";

const TABS: { id: TabId; label: string; Icon: typeof Activity }[] = [
  { id: "monitor", label: "Monitor IoT & Cloud", Icon: Activity },
  { id: "predict", label: "Predição IA (ML + MLP)", Icon: Brain },
  { id: "stats", label: "Estatística (Base Real)", Icon: BarChart3 },
  { id: "security", label: "Segurança & LGPD", Icon: Shield },
];

export default function App() {
  const [tab, setTab] = useState<TabId>("monitor");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [occurrences, setOccurrences] = useState<Occurrence[]>([]);
  const [indicators, setIndicators] = useState<Indicators | null>(null);
  const [summary, setSummary] = useState<StatsSummaryResponse | null>(null);
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [apiOnline, setApiOnline] = useState(false);

  const loadAll = useCallback(async () => {
    try {
      const [h, occ, ind, sum, aud] = await Promise.all([
        api.health(),
        api.listOcorrencias(),
        api.indicadores(),
        api.statsSummary(),
        api.securityAudit(),
      ]);
      setHealth(h);
      setOccurrences(occ);
      setIndicators(ind);
      setSummary(sum);
      setAudit(aud);
      setApiOnline(true);
    } catch {
      setApiOnline(false);
    }
  }, []);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-mark">RC</div>
            <div>
              <h1 className="brand-title">RespiraCidadão</h1>
              <p className="brand-sub">
                FIAP GS 2026.2 • Sala 1TIAPZ1 • Grupo Perceptron (CitizenTech)
              </p>
            </div>
          </div>

          <div className="status-pills">
            <span className={`pill ${apiOnline ? "ok" : "crit"}`}>
              API FastAPI: {apiOnline ? "Online" : "Offline"}
            </span>
            <span className={`pill ${health?.ml_carregado ? "ok" : "warn"}`}>
              ML (06): {health?.ml_carregado ? "Ativo" : "Pendente"}
            </span>
            <span className={`pill ${health?.nn_carregado ? "ok" : "warn"}`}>
              Rede Neural (08): {health?.nn_carregado ? "Ativa" : "Pendente"}
            </span>
          </div>
        </div>

        <nav className="nav-tabs" aria-label="Módulos integrados" role="tablist">
          {TABS.map(({ id, label, Icon }) => (
            <button
              key={id}
              type="button"
              role="tab"
              id={`tab-${id}`}
              aria-selected={tab === id}
              aria-controls="painel-principal"
              className={`tab-btn ${tab === id ? "active" : ""}`}
              onClick={() => setTab(id)}
            >
              <Icon size={16} aria-hidden="true" /> {label}
            </button>
          ))}
        </nav>
      </header>

      <main className="main-content" id="painel-principal" role="tabpanel" aria-labelledby={`tab-${tab}`}>
        {tab === "monitor" && (
          <MonitorTab occurrences={occurrences} indicators={indicators} onRefresh={loadAll} />
        )}
        {tab === "predict" && <PredictTab summary={summary} />}
        {tab === "stats" && <StatsTab summary={summary} />}
        {tab === "security" && <SecurityTab audit={audit} onRefresh={loadAll} />}
      </main>

      <footer className="footer-bar">
        Grupo Perceptron (1TIAPZ1) • Giovanni Hessel (RM 570574) • Suellen Silva (RM 573862) • Israel Toledo (RM 573854) • ODS 3, 10 e 11
      </footer>
    </div>
  );
}
