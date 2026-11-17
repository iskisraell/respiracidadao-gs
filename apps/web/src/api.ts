import type {
  AuditResponse,
  DeviceType,
  HealthResponse,
  Indicators,
  Occurrence,
  PredictInput,
  PredictResponse,
  RiskLevel,
  StatsSummaryResponse,
} from "./types";

const BASE = "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const text = await res.text();
  let data: Record<string, unknown> = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { erro: text.slice(0, 160) };
  }
  if (!res.ok) {
    const err = new Error(String(data.detail ?? data.erro ?? `HTTP ${res.status}`)) as Error & {
      status?: number;
      payload?: unknown;
    };
    err.status = res.status;
    err.payload = data;
    throw err;
  }
  return data as T;
}

export const api = {
  health: () => req<HealthResponse>("/health"),
  listOcorrencias: (risco?: string) =>
    req<Occurrence[]>(`/ocorrencias${risco && risco !== "todos" ? `?risco=${encodeURIComponent(risco)}` : ""}`),
  indicadores: () => req<Indicators>("/indicadores"),
  simulate: (cenario: "todos" | RiskLevel = "todos", tipo: DeviceType = "esp32") =>
    req<{ executados: number; resultados: unknown[] }>("/simulate", {
      method: "POST",
      body: JSON.stringify({ cenario, tipo }),
    }),
  createOcorrenciaRaw: async (payload: Record<string, unknown>) => {
    const res = await fetch(`${BASE}/ocorrencias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json().catch(() => ({}));
    return { status: res.status, body };
  },
  predict: (payload: PredictInput) =>
    req<PredictResponse>("/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  statsSummary: () => req<StatsSummaryResponse>("/stats/summary"),
  securityAudit: () => req<AuditResponse>("/security/audit?limit=30"),
  verifyIntegrity: (id: number) =>
    req<{ id: number; integro: boolean; hash_armazenado: string; hash_recalculado: string }>(
      `/security/verify/${id}`
    ),
  testClearWithKey: async (apiKey?: string) => {
    const headers: Record<string, string> = {};
    if (apiKey) headers["X-API-Key"] = apiKey;
    const res = await fetch(`${BASE}/ocorrencias`, { method: "DELETE", headers });
    const body = await res.json().catch(() => ({}));
    return { status: res.status, body };
  },
};
