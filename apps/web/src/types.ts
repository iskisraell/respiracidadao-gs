export type RiskLevel = "normal" | "atencao" | "critico";
export type DeviceType = "esp32" | "drone" | "app";

export interface HealthResponse {
  status: string;
  servico: string;
  modelo_sentimento: string;
  ia_hf_configurada: boolean;
  ml_carregado: boolean;
  nn_carregado: boolean;
  limiares: Record<string, [number, number]>;
}

export interface Occurrence {
  id: number;
  dispositivo_id: string;
  tipo: DeviceType;
  latitude: number | null;
  longitude: number | null;
  metrica: string;
  valor: number;
  temperatura_c: number | null;
  umidade_pct: number | null;
  relato: string;
  ia_sentimento: string;
  ia_confianca: number | null;
  ia_fonte: string;
  nivel_risco: RiskLevel;
  alerta: boolean;
  hash_integridade: string;
  criado_em: string;
}

export interface Indicators {
  total_leituras: number;
  total_alertas: number;
  pct_alertas: number;
  media_valor: number;
  max_valor: number;
  min_valor: number;
  por_risco: Record<string, number>;
  por_dispositivo: Record<string, number>;
}

export interface PredictInput {
  co_sensor_s1: number;
  c6h6_gt: number;
  nmhc_sensor_s2: number;
  nox_gt: number;
  nox_sensor_s3: number;
  no2_gt: number;
  no2_sensor_s4: number;
  o3_sensor_s5: number;
  temperatura_c: number;
  umidade_pct: number;
  umidade_absoluta: number;
}

export interface ModelVerdict {
  modelo: string;
  classe: RiskLevel;
  probabilidades: Record<RiskLevel, number>;
}

export interface PredictResponse {
  ml_disponivel: boolean;
  nn_disponivel: boolean;
  ml?: ModelVerdict;
  nn?: ModelVerdict;
  fallback_limiar?: { classe: RiskLevel };
}

export interface AuditEvent {
  timestamp: string;
  event: string;
  severity: string;
  client_ip: string;
  status_code: number;
  detail: string;
}

export interface AuditResponse {
  rate_limit: { max_requests: number; window_sec: number };
  controls: string[];
  events: AuditEvent[];
}

export interface StatsSummaryResponse {
  estatistica: {
    dataset: {
      nome: string;
      registros_brutos: number;
      registros_limpos: number;
      variavel_alvo: string;
      distribuicao_risco: Record<string, number>;
    };
    item_02_normal: {
      variavel: string;
      media: number;
      desvio_padrao: number;
      mediana: number;
      p_menor_media: number;
      classificacao_a: string;
      p_maior_mediana: number;
      classificacao_b: string;
    };
    item_03_testes_hipotese: {
      variavel: string;
      media_pop: number;
      sigma_pop: number;
      teste_3a_unilateral_esquerda: {
        n: number;
        alpha: number;
        media_amostral: number;
        z_calculado: number;
        z_critico: number;
        p_valor: number;
        rejeita_h0: boolean;
        decisao: string;
      };
      teste_3b_unilateral_direita: {
        n: number;
        alpha: number;
        media_amostral: number;
        z_calculado: number;
        z_critico: number;
        p_valor: number;
        rejeita_h0: boolean;
        decisao: string;
      };
    };
    item_04_regressao_simples: {
      x: string;
      y: string;
      covariancia: number;
      pearson_r: number;
      equacao: string;
      r2: number;
      teste_f: number;
      previsao_exemplo: { "PT08.S1(CO)": number; co_previsto: number };
    };
    item_05_regressao_multipla: {
      variaveis_explicativas: string[];
      equacao: string;
      r2: number;
      r2_ajustado: number;
      teste_f: number;
      previsoes: Array<{ cenario: string; co_previsto: number }>;
    };
    item_06_regressao_logistica: {
      equacao_logit: string;
      acuracia_teste: number;
      matriz_confusao: number[][];
      precision_critico: number;
      recall_critico: number;
      f1_critico: number;
    };
  } | null;
  machine_learning: {
    algoritmo_vencedor: string;
    cv_f1_macro: number;
    teste_accuracy: number;
    teste_f1_macro: number;
    comparacao_modelos: Array<{
      modelo: string;
      train_acc: number;
      test_acc: number;
      test_f1_macro: number;
      gap_overfit: number;
    }>;
    feature_importance: Array<{ feature: string; importance: number }>;
  } | null;
  redes_neurais: {
    arquitetura: string;
    teste_accuracy: number;
    teste_f1_macro: number;
    comparacao_experimentos: Array<{
      configuracao: string;
      epocas_executadas: number;
      train_acc: number;
      test_acc: number;
      test_f1_macro: number;
      gap_overfit: number;
    }>;
    curvas: {
      epocas: number[];
      train_loss: number[];
      val_loss: number[];
      train_acc: number[];
      val_acc: number[];
    };
  } | null;
}
