import type { Level } from "./types";

export const LEVEL_NAME: Record<Level, string> = { normal: "Bom", atencao: "Atenção", critico: "Ruim" };

export function ago(iso: string, now = Date.now()): string {
  const min = Math.max(0, Math.round((now - new Date(iso).getTime()) / 60000));
  if (min < 1) return "agora há pouco";
  if (min < 60) return `há ${min} min`;
  const h = Math.round(min / 60);
  return h < 24 ? `há ${h} h` : `há ${Math.round(h / 24)} dias`;
}

export const minutesSince = (iso: string) => (Date.now() - new Date(iso).getTime()) / 60000;

export const pct = (x: number) => `${Math.round(x * 100)}%`;

/** Nível de um sensor isolado, com os mesmos limiares da API. */
export function sensorLevel(valor: number, [low, high]: [number, number]): Level {
  return valor >= high ? "critico" : valor >= low ? "atencao" : "normal";
}

export const LIMITS = { gas_voc: [830, 1140] as [number, number], gas_co: [1010, 1280] as [number, number] };
