# 05 — Computational Thinking with Python (`Protótipo CitizenTech com Dados e IA`)

- **Portal ID:** `codigoTrabalho=28270`, `codigoTrabalhoGrupo=726405`
- **Prazo:** `19/11/2026 23:55:00` *(não entregue)*
  - **Recomendação explícita no portal:** *"Alunos, evitem problemas de sobrecarga, priorizem entregar a GS até às 17h do dia 19/nov."*
- **Formação:** Individual ou em grupo de até 3 participantes
- **Entrega:** Portal do Aluno
- **Enunciado original:** [`GS_2026_2_Computational_Thinking_Python_Fevereiro.pdf`](./enunciado/GS_2026_2_Computational_Thinking_Python_Fevereiro.pdf)

---

## Objetivo

Desenvolver uma **API REST em Python (Flask ou FastAPI)** integrada à solução de **AICSS (`02`)**, considerando o mesmo problema, público e contexto CitizenTech das demais disciplinas:

```
ESP32 com sensores ──► JSON ──► API REST Python ──► processamento ──► CSV ──► consulta GET
```

---

## Requisitos Técnicos

- [ ] **API REST com Flask ou FastAPI**
- [ ] **Endpoint `POST`** para receber leituras em JSON e **validar campos obrigatórios**
- [ ] Processamento usando **funções, estruturas condicionais, repetições e coleções**
- [ ] **Classificar as leituras** segundo regras ligadas ao problema CitizenTech
- [ ] **Persistir em CSV** com data/hora, valores e classificação
- [ ] **Endpoint `GET`** para consultar registros armazenados
- [ ] **Pelo menos 1 indicador calculado** (ex.: média, total de alertas ou valor máximo)
- [ ] **3 cenários de teste** demonstrados com requisições, respostas e registros no CSV
- [ ] JSON compatível com o ESP32/simulador de `02 - AICSS` *(interface gráfica, banco de dados e modelo de IA não são obrigatórios nesta entrega)*
- [ ] Identificar limitações da solução

---

## O Que Entregar

- [ ] Capa com título, nomes completos e RMs
- [ ] Problema, público beneficiado e contribuição da API
- [ ] Arquitetura, origem dos dados e **contrato JSON**
- [ ] Código Python e instruções de execução
- [ ] Testes dos endpoints, **3 cenários** e histórico **CSV**
- [ ] Indicador calculado, limitações e relação com **1 ODS**

---

## Critérios de Avaliação (10 pontos)

| Critério | Pontos |
|---|---:|
| Problema e contribuição CitizenTech | 1,0 |
| API REST e endpoints funcionais | 2,0 |
| Recebimento e processamento do JSON | 2,0 |
| Persistência CSV e consulta GET | 2,0 |
| Lógica, funções e indicador calculado | 2,0 |
| Testes e demonstração de integração | 1,0 |
| **Total** | **10,0** |

---

## Workspace / Notas de Trabalho

- **Framework escolhido (`FastAPI` / `Flask`):** `TODO`
- **Contrato JSON (`POST`):** `TODO`
- **Indicador calculado:** `TODO`
