-- RespiraCidadao: leituras dos sensores e relatos, gravados pela funcao na nuvem (RDS PostgreSQL)

CREATE TABLE IF NOT EXISTS ocorrencias (
    id                SERIAL PRIMARY KEY,
    dispositivo_id    TEXT        NOT NULL,
    tipo_dispositivo  TEXT        NOT NULL,              -- esp32 | app
    latitude          DOUBLE PRECISION,
    longitude         DOUBLE PRECISION,
    metrica           TEXT        NOT NULL,              -- gas_voc | gas_co
    valor             DOUBLE PRECISION NOT NULL,
    gas_co            DOUBLE PRECISION,                  -- indice de monoxido de carbono
    temperatura_c     DOUBLE PRECISION,
    umidade_pct       DOUBLE PRECISION,
    relato            TEXT,                              -- relato de quem esta no lugar, lido pela IA
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
SELECT id, dispositivo_id, tipo_dispositivo, metrica, valor, gas_co,
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
