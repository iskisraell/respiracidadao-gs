-- ============================================================================
-- 04 Cognitive Data Science (FIAP GS 2026.2) - Inclusive Mobility Rover (Oracle SQL)
-- Submissao INDIVIDUAL em: https://pt.surveymonkey.com/r/VQNNZZZ
-- Integrantes (Grupo Perceptron, Sala 1TIAPZ1):
--   * Giovanni Henrique Pereira Hessel (RM 570574)
--   * Suellen Pereira da Silva (RM 573862)
--   * Israel Carneiro de Toledo (RM 573854)
--
-- Colunas conferidas com o Dicionario de Dados e MER oficial de GS_2026_2SEM_1TIA(1).pdf:
--   AMBIENTES_ROVER (ID_AMBIENTE, NOME_AMBIENTE, TIPO_AMBIENTE)
--   ROBOS_ROVER     (ID_ROBO, NOME_ROBO, MODELO)
--   OPERACOES_ROVER (ID_OPERACAO, ID_ROBO, ID_AMBIENTE, DATA_OPERACAO)
--   DETECCOES_ROVER (ID_DETECCAO, ID_OPERACAO, TIPO_OBSTACULO, DISTANCIA_CM, CONFIANCA)
-- ============================================================================

-- Questao 1: Ambientes com multiplos robos e obstaculos proximos (< 100 cm)
SELECT
    a.nome_ambiente               AS AMBIENTE,
    COUNT(DISTINCT o.id_robo)     AS QTDE_ROBOS,
    ROUND(AVG(d.distancia_cm), 2) AS MEDIA_DISTANCIA
FROM AMBIENTES_ROVER a
JOIN OPERACOES_ROVER o ON o.id_ambiente = a.id_ambiente
JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
WHERE d.distancia_cm < 100
GROUP BY a.id_ambiente, a.nome_ambiente
HAVING COUNT(DISTINCT o.id_robo) >= 2
   AND AVG(d.distancia_cm) < 70
ORDER BY a.nome_ambiente ASC;


-- Questao 2: Robos com deteccoes de alta confianca (>= 80)
SELECT
    r.nome_robo                 AS ROBO,
    r.modelo                    AS MODELO,
    COUNT(d.id_deteccao)        AS QTDE_DETECCOES,
    ROUND(AVG(d.confianca), 2)  AS MEDIA_CONFIANCA
FROM ROBOS_ROVER r
JOIN OPERACOES_ROVER o ON o.id_robo     = r.id_robo
JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
WHERE d.confianca >= 80
GROUP BY r.id_robo, r.nome_robo, r.modelo
HAVING COUNT(d.id_deteccao) >= 3
   AND AVG(d.confianca) > 85
ORDER BY MEDIA_CONFIANCA DESC;


-- Questao 3: Tipos de obstaculo identificados em ambientes diferentes
SELECT
    d.tipo_obstaculo              AS TIPO_OBSTACULO,
    COUNT(DISTINCT o.id_ambiente) AS QTDE_AMBIENTES,
    COUNT(d.id_deteccao)          AS QTDE_DETECCOES,
    MIN(d.distancia_cm)           AS MENOR_DISTANCIA
FROM DETECCOES_ROVER d
JOIN OPERACOES_ROVER o ON o.id_operacao = d.id_operacao
GROUP BY d.tipo_obstaculo
HAVING COUNT(DISTINCT o.id_ambiente) >= 2
   AND COUNT(d.id_deteccao) >= 3
ORDER BY QTDE_AMBIENTES DESC, d.tipo_obstaculo ASC;


-- Questao 4: Operacoes com multiplos obstaculos (>= 3) e distancia critica (< 80 cm)
SELECT
    o.id_operacao                 AS ID_OPERACAO,
    r.nome_robo                   AS ROBO,
    a.nome_ambiente               AS AMBIENTE,
    COUNT(d.id_deteccao)          AS QTDE_DETECCOES,
    ROUND(AVG(d.distancia_cm), 2) AS MEDIA_DISTANCIA
FROM OPERACOES_ROVER o
JOIN ROBOS_ROVER     r ON r.id_robo     = o.id_robo
JOIN AMBIENTES_ROVER a ON a.id_ambiente = o.id_ambiente
JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
GROUP BY o.id_operacao, r.nome_robo, a.nome_ambiente
HAVING COUNT(d.id_deteccao) >= 3
   AND AVG(d.distancia_cm) < 80
ORDER BY MEDIA_DISTANCIA ASC, o.id_operacao ASC;


-- Questao 5: Ambientes monitorados, inclusive sem operacoes ou sem deteccoes
SELECT
    a.nome_ambiente               AS AMBIENTE,
    COUNT(DISTINCT o.id_operacao) AS QTDE_OPERACOES,
    COUNT(d.id_deteccao)          AS QTDE_DETECCOES
FROM AMBIENTES_ROVER a
LEFT JOIN OPERACOES_ROVER o ON o.id_ambiente = a.id_ambiente
LEFT JOIN DETECCOES_ROVER d ON d.id_operacao = o.id_operacao
GROUP BY a.id_ambiente, a.nome_ambiente
ORDER BY a.nome_ambiente ASC;
