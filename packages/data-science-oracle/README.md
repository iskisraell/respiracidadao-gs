# 04: Cognitive Data Science, Inclusive Mobility Rover

Esta disciplina é independente do projeto RespiraCidadão e exige envio individual no formulário SurveyMonkey:
`https://pt.surveymonkey.com/r/VQNNZZZ`

## Consultas prontas e conferidas

Os nomes exatos das tabelas e colunas foram conferidos com o Dicionário de Dados e o Modelo Entidade-Relacionamento oficial de `GS_2026_2SEM_1TIA(1).pdf`:

- `AMBIENTES_ROVER`: `ID_AMBIENTE`, `NOME_AMBIENTE`, `TIPO_AMBIENTE`
- `ROBOS_ROVER`: `ID_ROBO`, `NOME_ROBO`, `MODELO`
- `OPERACOES_ROVER`: `ID_OPERACAO`, `ID_ROBO`, `ID_AMBIENTE`, `DATA_OPERACAO`
- `DETECCOES_ROVER`: `ID_DETECCAO`, `ID_OPERACAO`, `TIPO_OBSTACULO`, `DISTANCIA_CM`, `CONFIANCA`

Todas as cinco consultas de [`queries_inclusive_mobility_rover.sql`](./queries_inclusive_mobility_rover.sql) já usam essas colunas e os apelidos exatos exigidos pelo enunciado (`AMBIENTE`, `QTDE_ROBOS`, `MEDIA_DISTANCIA`, `ROBO`, `MODELO`, `QTDE_DETECCOES`, `MEDIA_CONFIANCA`, `TIPO_OBSTACULO`, `QTDE_AMBIENTES`, `MENOR_DISTANCIA`, `ID_OPERACAO`, `QTDE_OPERACOES`).

## Envio individual

Cada integrante do grupo, Giovanni RM 570574, Suellen RM 573862 e Israel RM 573854, deve copiar e colar as cinco consultas individualmente no SurveyMonkey usando o RM só com números e o nome completo sem abreviações. Não suba nenhum arquivo no Portal dessa disciplina.
