export type Level = "normal" | "atencao" | "critico";

export interface Reading {
  id: number;
  dispositivo_id: string;
  metrica: "gas_voc" | "gas_co";
  valor: number;
  gas_co: number | null;
  temperatura_c: number | null;
  umidade_pct: number | null;
  nivel_risco: Level;
  ia_risco: Level | null;
  ia_risco_prob: number | null;
  hash_integridade: string;
  criado_em: string;
}

export interface Report {
  id: number;
  local_id: string;
  texto: string;
  urgente: boolean;
  criado_em: string;
}

export interface Place {
  id: string;
  nome: string;
  tipo: "escola" | "ubs" | "praca";
  bairro: string;
  nivel: Level | null;
  orientacao: { titulo: string; frase: string; acoes: string[] } | null;
  ultima_leitura: Reading | null;
  historico: { valor: number; nivel: Level; criado_em: string }[];
  relatos: Report[];
}

export interface HourPattern {
  horas: { hora: number; normal: number; atencao: number; critico: number }[];
  melhor_janela: { inicio: number; fim: number; critico_medio: number; pior_hora: number; pior_critico: number };
}

export interface Verdict {
  classe: Level;
  probabilidades: Record<Level, number>;
}

export interface PredictResult {
  ml?: Verdict;
  nn?: Verdict;
  regra_local: { classe: Level };
}

export interface ModelSummary {
  machine_learning: {
    teste_accuracy: number;
    split_temporal_accuracy: number;
    comparacao_conjuntos: { conjunto: string; accuracy: number; f1_macro: number }[];
  } | null;
}
