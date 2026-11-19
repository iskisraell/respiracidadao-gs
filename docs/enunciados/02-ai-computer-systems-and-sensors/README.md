# 02 — AI Computer Systems & Sensors (`GS2026.2 - AICSS`)

- **Portal ID:** `codigoTrabalho=28651`, `codigoTrabalhoGrupo=737981`
- **Prazo:** `19/11/2026 23:55:00` *(não entregue)*
- **Formação:** Individual ou em grupo de até 3 participantes
- **Entrega:** Portal do Aluno
- **Enunciado original:** [`GS - 2026.2 - AICSS - FEV-1TIAP(F-Y-Z)-2026(1).pdf`](./enunciado/GS%20-%202026.2%20-%20AICSS%20-%20FEV-1TIAP(F-Y-Z)-2026(1).pdf)

---

## Objetivo

Construir e demonstrar o dispositivo IoT que coleta os dados do mesmo problema/público CitizenTech das demais disciplinas, seguindo o fluxo funcional:

```
Fenômeno observado ──► ESP32 com sensores ──► alerta local ──► JSON ──► servidor Python
```

O dispositivo alerta o cidadão localmente e envia as leituras em JSON para a solução integrada (onde serão gravadas em CSV e usadas pela IA das outras disciplinas).

---

## Requisitos Técnicos da Solução

- [ ] **ESP32 físico ou simulado no Wokwi**
- [ ] **Pelo menos 2 sensores** relevantes ao problema escolhido
- [ ] **Pelo menos 1 atuador** (LED, buzzer, display, etc.) para alerta local
- [ ] Coletar leituras, controlar limiares e classificar cada leitura/sensor com um status (ex.: `OK` / `ALERTA`)
- [ ] Transmitir as leituras em **JSON** para um **servidor Python** *(alinhar o formato JSON com `05 - Computational Thinking with Python` e `07 - Cloud`!)*
- [ ] Servidor Python exibe e grava os dados recebidos em **CSV**
- [ ] Demonstrar **pelo menos 3 comportamentos diferentes**, mostrando:
  1. Reação do atuador local
  2. JSON transmitido
  3. Registro salvo no servidor Python / CSV
- [ ] Identificar claramente o que foi implementado vs. simulado e explicar as limitações

---

## O Que Entregar no Documento / Pacote

- [ ] Capa com título, nomes completos e RMs
- [ ] Problema, público beneficiado e evidência de relevância
- [ ] Arquitetura da solução e origem dos dados
- [ ] Evidências de funcionamento, resultados dos testes com diferentes entradas (3+ comportamentos) e limitações identificadas
- [ ] Código desenvolvido (firmware ESP32/Wokwi + servidor Python)
- [ ] Relação com pelo menos **1 ODS**

---

## Critérios de Avaliação (10 pontos)

| Critério | Pontos |
|---|---:|
| Problema e contribuição CitizenTech | 1,0 |
| Coleta e decisão com dados IoT | 3,0 |
| Transmissão de dados usando JSON | 3,0 |
| Justificativa dos sensores utilizados e alinhamento com a solução adotada | 2,0 |
| Inovação apresentada | 1,0 |
| **Total** | **10,0** |

---

## Workspace / Notas de Trabalho

- **Link Wokwi (se simulado):** `TODO`
- **Sensores escolhidos (>=2):** `TODO`
- **Atuador escolhido (>=1):** `TODO`
- **Contrato JSON acordado com `05-Python` e `07-Cloud`:** `TODO`
