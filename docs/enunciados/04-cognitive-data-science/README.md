# 04 — Cognitive Data Science (`GS2026.2`)

- **Portal ID:** `codigoTrabalho=28907`, `codigoTrabalhoGrupo=745742`
- **Prazo:** `19/11/2026 23:55:00` *(não entregue)*
- **Onde entregar:** **SurveyMonkey:** [`https://pt.surveymonkey.com/r/VQNNZZZ`](https://pt.surveymonkey.com/r/VQNNZZZ)
  - **Aviso no portal FIAP:** *"Postar as respostas em: https://pt.surveymonkey.com/r/VQNNZZZ — Aqui não precisa postar nada!"*
- **Formação:** Pode ser resolvida em grupo de até 3 alunos, mas **ATENÇÃO: A ENTREGA É INDIVIDUAL** no formulário SurveyMonkey.

> **Atenção:** Esta disciplina é **standalone** (não usa o tema escolhido do grupo — usa o cenário **Inclusive Mobility Rover** em **Oracle Database**).

---

## Instruções Gerais

- **Valor total:** `10,0 pontos` — 5 consultas SQL, valendo **2,0 pontos cada**.
- Todas as consultas devem ser compatíveis com **Oracle Database**.
- Baixar o script `CRIACAO_CARGA_ORACLE.sql` na área de **Apostilas** do Portal do Aluno FIAP e executá-lo antes de iniciar.
- Entregar o **código SQL completo** de cada consulta no SurveyMonkey, com os **apelidos de coluna (aliases) exatamente como solicitados**.
- Campos obrigatórios do SurveyMonkey: **RM (somente números)** e **NOME completo (sem abreviar)**.

### Cenário e Tabelas (`Inclusive Mobility Rover`)
Protótipo robótico de apoio à mobilidade e mapeamento de obstáculos. As tabelas criadas por `CRIACAO_CARGA_ORACLE.sql` são:
- `AMBIENTES_ROVER`
- `ROBOS_ROVER`
- `OPERACOES_ROVER`
- `DETECCOES_ROVER`

---

## As 5 Consultas Solicitadas (Extraídas do SurveyMonkey)

### Questão 1 — Ambientes com múltiplos robôs e obstáculos próximos *(2,0 pts)*
- Exibir: nome do ambiente, quantidade de **robôs distintos** que realizaram detecções nesse ambiente e distância média (em cm) dos obstáculos detectados.
- Filtro de detecções: distância **inferior a 100 cm** (`< 100`).
- Filtro de grupos (`HAVING`): ambientes com **pelo menos 2 robôs distintos** (`>= 2`) e **distância média inferior a 70 cm** (`< 70`).
- Ordenação: nome do ambiente em ordem **alfabética** (`ASC`).
- **Aliases exatos:** `AMBIENTE`, `QTDE_ROBOS`, `MEDIA_DISTANCIA`

### Questão 2 — Robôs com detecções de alta confiança *(2,0 pts)*
- Exibir: nome do robô, modelo, quantidade de detecções registradas e confiança média das detecções.
- Filtro de detecções: confiança **maior ou igual a 80** (`>= 80`).
- Filtro de grupos (`HAVING`): robôs com **pelo menos 3 detecções** nessas condições (`>= 3`) e **confiança média superior a 85** (`> 85`).
- Ordenação: confiança média em ordem **decrescente** (`DESC`).
- **Aliases exatos:** `ROBO`, `MODELO`, `QTDE_DETECCOES`, `MEDIA_CONFIANCA`

### Questão 3 — Tipos de obstáculo identificados em ambientes diferentes *(2,0 pts)*
- Exibir: tipo do obstáculo, quantidade de **ambientes distintos** onde foi identificado, quantidade total de detecções e menor distância registrada.
- Filtro de grupos (`HAVING`): tipos detectados em **pelo menos 2 ambientes distintos** (`>= 2`) e com **3 ou mais detecções** (`>= 3`).
- Atenção: mais de uma detecção do mesmo tipo no mesmo ambiente não pode inflar a contagem de ambientes (`COUNT(DISTINCT ...)`).
- Ordenação: quantidade de ambientes distintos **decrescente** (`DESC`), depois tipo do obstáculo em ordem **alfabética** (`ASC`).
- **Aliases exatos:** `TIPO_OBSTACULO`, `QTDE_AMBIENTES`, `QTDE_DETECCOES`, `MENOR_DISTANCIA`

### Questão 4 — Operações com múltiplos obstáculos e distância crítica *(2,0 pts)*
- Exibir: identificador da operação, nome do robô, nome do ambiente, quantidade de detecções e distância média registrada.
- Filtro de grupos (`HAVING`): operações com **pelo menos 3 detecções** (`>= 3`) e **distância média inferior a 80 cm** (`< 80`).
- Ordenação: distância média em ordem **crescente** (`ASC`), depois identificador da operação (`ASC`).
- **Aliases exatos:** `ID_OPERACAO`, `ROBO`, `AMBIENTE`, `QTDE_DETECCOES`, `MEDIA_DISTANCIA`

### Questão 5 — Ambientes monitorados, inclusive sem obstáculos detectados *(2,0 pts)*
- Exibir: nome de **cada** ambiente, quantidade de operações registradas e quantidade de detecções vinculadas a essas operações.
- Todos os ambientes cadastrados devem aparecer, inclusive sem operações ou sem detecções (`LEFT JOIN`).
- Atenção: a contagem das operações **não pode ser inflada** quando uma mesma operação possui várias detecções (`COUNT(DISTINCT ...)`).
- Ordenação: nome do ambiente em ordem **alfabética** (`ASC`).
- **Aliases exatos:** `AMBIENTE`, `QTDE_OPERACOES`, `QTDE_DETECCOES`

---

## Checklist de Entrega

- [ ] Baixar `CRIACAO_CARGA_ORACLE.sql` nas Apostilas do Portal FIAP
- [ ] Executar no Oracle Database e inspecionar nomes exatos de colunas/PKs/FKs
- [ ] Escrever e validar as 5 queries (conferir aliases exatos e regras de `COUNT(DISTINCT ...)`)
- [ ] Submeter individualmente em [`https://pt.surveymonkey.com/r/VQNNZZZ`](https://pt.surveymonkey.com/r/VQNNZZZ) com RM `573854` e nome completo
