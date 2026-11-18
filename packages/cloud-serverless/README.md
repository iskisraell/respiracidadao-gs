# RespiraCidadão: Camada Serverless (`07 - Cloud Computing`)

## Cenário CitizenTech e Cidadão Beneficiado

O RespiraCidadão coleta telemetria de fumaça (`fumaca_ppm`), monóxido de carbono (`co_mg_m3`) e dióxido de nitrogênio (`no2_ug_m3`) com nós ESP32, drones e relatos textuais do cidadão, protegendo **crianças em escolas públicas, idosos e pacientes respiratórios crônicos** em periferias e áreas afetadas por queimadas urbanas e rurais.

### Limiares Locais Determinísticos

| Métrica | Normal | Atenção | Crítico (Alerta) |
|---|---|---|---|
| `fumaca_ppm` | `< 120` | `120 a 249.9` | `>= 250` |
| `co_mg_m3` | `< 4.0` | `4.0 a 8.9` | `>= 9.0` |
| `no2_ug_m3` | `< 100` | `100 a 199.9` | `>= 200` |

## Arquitetura AWS (Sem VPC na Lambda)

```text
ESP32 / Drone / Simulador
   │ HTTPS POST /ocorrencias
   ▼
AWS Lambda + Function URL (fora da VPC, timeout 30s)
   ├──► CloudWatch Logs (PAYLOAD RECEBIDO, DISPOSITIVO, CLASSIFICACAO, WARNING em critico/400)
   ├──► Hugging Face Router (https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-xlm-roberta-base-sentiment)
   ▼
Amazon RDS PostgreSQL (tabela ocorrencias)
```

### Justificativa da Camada de IA e Resiliência

O modelo `cardiffnlp/twitter-xlm-roberta-base-sentiment` via `router.huggingface.co` (autenticado pela variável de ambiente `HF_TOKEN`) interpreta o relato em português do cidadão. Caso o endpoint externo falhe ou atinja timeout, a exceção gera apenas um log `WARNING` e a Lambda grava a leitura normalmente usando a classificação local por limiares.

> **`alerta`:** a Lambda segue o starter oficial (`alerta = true` apenas em `critico`); a API FastAPI do monorepo também dispara `alerta` em `atencao` (aviso preventivo ao cidadão). Os **limiares são idênticos**.

### Validação e Resiliência (o que vira `400`, nunca `500`)

JSON inválido, corpo que não é objeto, `dispositivo_id`/`metrica`/`valor` ausentes ou vazios, `valor`/`latitude`/`longitude` não numéricos (ou `NaN`/`inf`) e `tipo_dispositivo` fora de `esp32 | drone | app`. Cada descarte sai como `WARNING` no CloudWatch. `medido_em` inválido cai para o horário do servidor, e uma resposta malformada da IA (ex.: `{"error": ...}` com HTTP 200) apenas gera `WARNING`: a leitura é classificada por limiar e gravada normalmente. Erros internos retornam mensagem genérica; o detalhe fica só no CloudWatch.

## Publicar na AWS (passo a passo)

1. **RDS PostgreSQL:** crie a instância (Security Group liberando `5432` para a Lambda) e execute `psql -h <endpoint-rds> -U <usuario> -d <banco> -f tabela_ocorrencias.sql`.
2. **Pacote:** `pip install -r requirements.txt -t pacote/ && cp lambda_function.py pacote/ && (cd pacote && zip -r ../funcao.zip .)`.
3. **Lambda:** runtime Python 3.12, **fora de VPC**, timeout **30 s**, `aws lambda update-function-code --function-name <nome> --zip-file fileb://funcao.zip`, handler `lambda_function.lambda_handler`, Function URL com auth `NONE`.
4. **Variáveis de ambiente (print 1):** `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `HF_TOKEN` (token *Read* do Hugging Face; nunca no código ou no repositório).
5. **Simulador (print 2):** `FUNCTION_URL=https://<id>.lambda-url.<regiao>.on.aws python3 simulador_dispositivo.py --cenario normal` e depois `--cenario queimada` (cruza `250 ppm` na 5ª leitura).
6. **CloudWatch (print 3) e RDS (print 4):** procure `PAYLOAD RECEBIDO`, `CLASSIFICACAO` e `GRAVADO NO RDS`; rode os `SELECT` ao final de `tabela_ocorrencias.sql`.

## Reprodução Local

```bash
python3 teste_local.py   # 8 verificações: 400/201, IA com falha, entradas inválidas, base64
# Em dois terminais:
python3 servidor_local.py
FUNCTION_URL=http://127.0.0.1:8099 python3 simulador_dispositivo.py --cenario queimada --leituras 5 --intervalo 0.5
```

## ODS Relacionados

- **ODS 3:** Saúde e Bem-Estar (prevenção de agravos respiratórios).
- **ODS 10 e 11:** Redução das desigualdades e comunidades sustentáveis.
