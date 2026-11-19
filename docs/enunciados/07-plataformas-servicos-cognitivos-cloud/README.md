# 07 — Plataformas, Serviços Cognitivos & Cloud Computing (`Computação Serverless`)

- **Portal ID:** `codigoTrabalho=28952`, `codigoTrabalhoGrupo=747101`
- **Prazo:** `19/11/2026 23:55:00` *(não entregue)*
- **Entrega:** Portal do Aluno
- **Starter Kit Oficial extraído em:** [`./starter/`](./starter/) *(contém `enunciado_gs_citizentech.md`, `lambda_function.py`, `simulador_dispositivo.py`, `servidor_local.py`, `esp32_citizentech.ino`, `tabela_ocorrencias.sql`, `teste_local.py`, `LEIAME.txt`)*

---

## Objetivo e Arquitetura

Construir a camada serverless na **AWS** que ingere leituras de campo (ESP32, drone ou app), registra telemetria no **CloudWatch Logs**, classifica o risco localmente e analisa o relato textual via **IA por API**, persistindo no **Amazon RDS PostgreSQL**:

```
ESP32 / drone / app (real ou simulador Python)
    │  HTTPS POST {dispositivo_id, tipo, latitude, longitude, metrica, valor, relato}
    ▼
AWS Lambda + Function URL  (POST /ocorrencias, GET /ocorrencias, GET /health)
    ├──► CloudWatch Logs (payload bruto, interpretado, classificação, id; WARNING p/ inválidos/críticos)
    ├──► IA Externa (Hugging Face router ou Amazon Comprehend — falha NÃO derruba ingestão)
    ▼
Amazon RDS PostgreSQL  (tabela ocorrencias)
```

> **Pré-requisito crítico AWS:** A Lambda **NÃO deve ficar dentro de VPC**, para ter saída para internet sem NAT Gateway. Se você já tem `challenge-api`, reaproveite a base!

---

## Requisitos Obrigatórios

1. **Cenário CitizenTech no README:** problema, cidadão beneficiado, métrica medida, limiares de risco (`normal`, `atencao`, `critico`) e conexão com os ODS (ex.: ODS 3, 10, 11).
2. **Tabela `ocorrencias` no RDS PostgreSQL:** `dispositivo_id`, `tipo`, coordenadas (`latitude`/`longitude`), `metrica`, `valor`, `relato`, resultado da análise de IA, nível de risco e data/hora (`tabela_ocorrencias.sql` está em `./starter/`).
3. **Rotas na Lambda:**
   - `POST /ocorrencias`: lê JSON, valida obrigatórios (`dispositivo_id`, `metrica`, `valor`), retorna `400` se faltar campo e `201` com `{id, nivel_risco, alerta, ...}` no sucesso.
   - `GET /health` mantido + `GET /ocorrencias` listando registros gravados.
4. **Logs claros no CloudWatch:** linhas separadas/legíveis para payload bruto, dados interpretados, resultado da classificação e `id` gravado; leituras inválidas e críticas logadas como `WARNING`.
5. **Classificação local de risco:** `normal`, `atencao`, `critico` (independente de rede).
6. **Camada de IA (sem segredo no código):**
   - **Caminho A — Hugging Face (recomendado):** token Read na env `HF_TOKEN`, modelo `cardiffnlp/twitter-xlm-roberta-base-sentiment`, endpoint `https://router.huggingface.co/hf-inference/models/{modelo}` *(o antigo `api-inference.huggingface.co` dá erro 410)*, timeout da Lambda = **30s**, usando apenas `urllib`.
   - **Caminho B — Amazon Comprehend:** política `ComprehendReadOnly` na role da Lambda, idioma `pt`.
   - **Resiliência:** se a IA falhar/der timeout, a ingestão continua normalmente (classificação por limiar + gravação no RDS + log).
7. **Simulador de dispositivo (ou firmware ESP32):** enviar sequência de leituras evoluindo até cruzar o limiar crítico, imprimindo o que enviou e a resposta da API.
8. **Teste ponta a ponta:** cenário normal + cenário crítico comprovados no CloudWatch e no RDS.

---

## Entregáveis

- [ ] **Function URL** da Lambda em funcionamento
- [ ] **Endpoint do RDS PostgreSQL** *(sem a senha!)*
- [ ] **Script SQL** de criação da tabela `ocorrencias`
- [ ] **Código final** da função Lambda + código do simulador (ou firmware ESP32)
- [ ] **4 evidências em imagem (prints):**
  1. Variável de ambiente cadastrada (ex.: `HF_TOKEN` / `DB_*`)
  2. Simulador enviando as leituras
  3. Trecho do CloudWatch Logs com payload chegando e classificação
  4. Consulta no banco com as ocorrências gravadas
- [ ] **README** com cenário CitizenTech, cidadão beneficiado, limiares, caminho de IA escolhido e justificativa, ODS e passo a passo de reprodução
- [ ] **Vídeo de até 5 minutos** demonstrando simulador enviando dados, CloudWatch recebendo e RDS gravando

---

## Critérios de Avaliação (100%)

| Critério | Peso |
|---|---:|
| Ingestão funcionando (`POST` recebendo, validando e respondendo) | 25% |
| Observabilidade (log claro do que chega, classifica e descarta) | 20% |
| Persistência (modelo coerente e gravação consistente no RDS) | 20% |
| Camada de IA integrada (token protegido e falha tratada sem derrubar ingestão) | 15% |
| Simulador do dispositivo e teste de ponta a ponta | 10% |
| Aderência ao CitizenTech (problema real, cidadão identificado, ODS) | 10% |

---

## Como Testar Localmente Agora (Starter Kit)

No diretório [`./starter/`](./starter/):
```bash
# Terminal 1
python3 servidor_local.py
# Terminal 2
FUNCTION_URL=http://127.0.0.1:8099 python3 simulador_dispositivo.py --cenario enchente --leituras 5 --intervalo 1
```
