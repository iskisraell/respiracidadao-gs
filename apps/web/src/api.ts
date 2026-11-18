import type { HourPattern, Level, ModelSummary, Place, PredictResult, Report } from "./types";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, { ...init, headers: { "Content-Type": "application/json" } });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = res.status === 429 ? "Muitos envios seguidos. Espere um minuto." : data.detail ?? data.erro;
    throw new Error(typeof msg === "string" ? msg : "Não deu certo. Tente de novo.");
  }
  return data as T;
}

const post = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });

export const api = {
  places: () => req<Place[]>("/locais"),
  hours: () => req<HourPattern>("/padrao-horario"),
  report: (local_id: string, texto: string) => req<Report>("/relatos", post({ local_id, texto })),
  demo: (local_id: string, cenario: Level) => req("/simulate", post({ local_id, cenario })),
  predict: (r: { gas_co: number; gas_voc: number; temperatura_c: number; umidade_pct: number }) =>
    req<PredictResult>("/predict", post(r)),
  summary: () => req<ModelSummary>("/stats/summary"),
  verify: (id: number) => req<{ integro: boolean }>(`/security/verify/${id}`),
};
