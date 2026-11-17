-- RespiraCidadao - FIAP GS 2026.2 (07 Cloud Computing)
-- Tabela no Amazon RDS PostgreSQL para ingestao serverless de ocorrencias respiratorias

CREATE TABLE IF NOT EXISTS ocorrencias (
    id                SERIAL PRIMARY KEY,
    dispositivo_id    TEXT        NOT NULL,
    tipo_dispositivo  TEXT        NOT NULL,              -- esp32 | drone | app
    latitude          DOUBLE PRECISION,
    longitude         DOUBLE PRECISION,
    metrica           TEXT        NOT NULL,              -- fumaca_ppm | co_mg_m3 | no2_ug_m3
    valor             DOUBLE PRECISION NOT NULL,
    relato            TEXT,                              -- texto do cidadao analisado via HF Router
    sentimento        TEXT,                              -- rotulo retornado pela IA
    confianca         NUMERIC(5,4),                      -- score da IA
    nivel_risco       TEXT        NOT NULL,              -- normal | atencao | critico | desconhecido
    medido_em         TIMESTAMPTZ,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocorrencias_dispositivo ON ocorrencias (dispositivo_id);
CREATE INDEX IF NOT EXISTS idx_ocorrencias_risco       ON ocorrencias (nivel_risco);
CREATE INDEX IF NOT EXISTS idx_ocorrencias_criado      ON ocorrencias (criado_em DESC);

-- Consultas de verificacao (evidencia RDS)
SELECT id, dispositivo_id, tipo_dispositivo, metrica, valor,
       nivel_risco, sentimento, confianca, criado_em
  FROM ocorrencias
 ORDER BY id DESC
 LIMIT 10;

SELECT dispositivo_id, metrica, valor, relato, sentimento, criado_em
  FROM ocorrencias
 WHERE nivel_risco = 'critico'
 ORDER BY criado_em DESC;

SELECT dispositivo_id,
       COUNT(*)                              AS leituras,
       ROUND(AVG(valor)::numeric, 2)         AS media,
       MAX(valor)                            AS pico,
       SUM((nivel_risco = 'critico')::int)   AS criticas
  FROM ocorrencias
 GROUP BY dispositivo_id
 ORDER BY criticas DESC, leituras DESC;
