-- ============================================================================
-- 04 Cognitive Data Science (FIAP GS 2026.2) - Inclusive Mobility Rover (Oracle SQL)
-- Submissao INDIVIDUAL em: https://pt.surveymonkey.com/r/VQNNZZZ
-- Integrantes (Grupo Perceptron, Sala 1TIAPZ1):
--   * Giovanni Henrique Pereira Hessel (RM 570574)
--   * Suellen Pereira da Silva (RM 573862)
--   * Israel Carneiro de Toledo (RM 573854)
--
-- ATENCAO: Antes de enviar no SurveyMonkey, confirme os nomes exatos das colunas
-- de ligacao (PK/FK, ex.: id_ambiente / ambiente_id / distancia_cm / confianca)
-- no arquivo CRIACAO_CARGA_ORACLE.sql disponivel em Apostilas no Portal FIAP.
-- Os aliases de saida abaixo ja seguem exatamente o enunciado.
-- ============================================================================

-- Questao 1: Ambientes com multiplos robos e obstaculos proximos (< 100 cm)
SELECT
    a.nome                        AS AMBIENTE,
    COUNT(DISTINCT r.id_robo)     AS QTDE_ROBOS,
    ROUND(AVG(d.distancia_cm), 2) AS MEDIA_DISTANCIA
FROM AMBIENTES_ROVER a
JOIN OPERACOES_ROVER o ON o.id_ambiente = a.id_ambiente
JOIN ROBOS_ROVER     r ON r.id_robo     = o.id_robo
JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
WHERE d.distancia_cm < 100
GROUP BY a.id_ambiente, a.nome
HAVING COUNT(DISTINCT r.id_robo) >= 2
   AND AVG(d.distancia_cm) < 70
ORDER BY AMBIENTE ASC;


-- Questao 2: Robos com deteccoes de alta confianca (>= 80)
SELECT
    r.nome                      AS ROBO,
    r.modelo                    AS MODELO,
    COUNT(d.id_deteccao)        AS QTDE_DETECCOES,
    ROUND(AVG(d.confianca), 2)  AS MEDIA_CONFIANCA
FROM ROBOS_ROVER r
JOIN OPERACOES_ROVER o ON o.id_robo     = r.id_robo
JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
WHERE d.confianca >= 80
GROUP BY r.id_robo, r.nome, r.modelo
HAVING COUNT(d.id_deteccao) >= 3
   AND AVG(d.confianca) > 85
ORDER BY MEDIA_CONFIANCA DESC;


-- Questao 3: Tipos de obstaculo identificados em ambientes diferentes
SELECT
    d.tipo_obstaculo             AS TIPO_OBSTACULO,
    COUNT(DISTINCT o.id_ambiente) AS QTDE_AMBIENTES,
    COUNT(d.id_deteccao)         AS QTDE_DETECCOES,
    MIN(d.distancia_cm)          AS MENOR_DISTANCIA
FROM DETECCOES_ROVER d
JOIN OPERACOES_ROVER o ON o.id_operacao = d.id_operacao
GROUP BY d.tipo_obstaculo
HAVING COUNT(DISTINCT o.id_ambiente) >= 2
   AND COUNT(d.id_deteccao) >= 3
ORDER BY QTDE_AMBIENTES DESC, TIPO_OBSTACULO ASC;


-- Questao 4: Operacoes com multiplos obstaculos (>= 3) e distancia critica (< 80 cm)
SELECT
    o.id_operacao                 AS ID_OPERACAO,
    r.nome                        AS ROBO,
    a.nome                        AS AMBIENTE,
    COUNT(d.id_deteccao)          AS QTDE_DETECCOES,
    ROUND(AVG(d.distancia_cm), 2) AS MEDIA_DISTANCIA
FROM OPERACOES_ROVER o
JOIN ROBOS_ROVER     r ON r.id_robo     = o.id_robo
JOIN AMBIENTES_ROVER a ON a.id_ambiente = o.id_ambiente
JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
GROUP BY o.id_operacao, r.id_robo, r.nome, a.id_ambiente, a.nome
HAVING COUNT(d.id_deteccao) >= 3
   AND AVG(d.distancia_cm) < 80
ORDER BY MEDIA_DISTANCIA ASC, ID_OPERACAO ASC;


-- Questao 5: Ambientes monitorados, inclusive sem operacoes/deteccoes
SELECT
    a.nome                        AS AMBIENTE,
    COUNT(DISTINCT o.id_operacao) AS QTDE_OPERACOES,
    COUNT(d.id_deteccao)          AS QTDE_DETECCOES
FROM AMBIENTES_ROVER a
LEFT JOIN OPERACOES_ROVER o ON o.id_ambiente = a.id_ambiente
LEFT JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
GROUP BY a.id_ambiente, a.nome
ORDER BY AMBIENTE ASC;
