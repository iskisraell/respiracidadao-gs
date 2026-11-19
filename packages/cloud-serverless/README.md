# Central do RespiraCidadão na nuvem (AWS)

A central é quem recebe a leitura do sensor, decide o nível, registra telemetria no CloudWatch, aciona a camada de IA para relatos e guarda o histórico no PostgreSQL gerenciado. No dia a dia ela roda como a API do repositório (`apps/api`). Esta pasta é a mesma central em formato serverless na AWS, operando sem servidor ligado o tempo todo:

```text
sensor ESP32 / simulador --HTTPS--> AWS Lambda (Function URL, fora da VPC) --> Amazon RDS PostgreSQL 18.3 (SSL + KMS)
                                         |--> CloudWatch Logs: payload bruto, validacao, classificacao, WARNING, id gravado
                                         '--> IA de texto (Hugging Face router): le o relato sem derrubar a ingestao
```

## Ambiente publicado e validado na AWS (us-east-1)

- **Function URL da Lambda (`respiracidadao-central`):** `https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws/`
- **Endpoint do Amazon RDS PostgreSQL 18.3 (`respiracidadao-db`, sem senha):** `respiracidadao-db.co6giv33mf2r.us-east-1.rds.amazonaws.com` (porta `5432`, banco `respiracidadao`, usuário `respira`, SSL obrigatório, `StorageEncrypted=True`)
- **Log Group no CloudWatch:** `/aws/lambda/respiracidadao-central`
- **Runtime e limites:** Python 3.12, 256 MB, timeout de 30s, **fora da VPC** (saída direta para internet sem custo de NAT Gateway), execução via `LabRole`.

## Cenário CitizenTech, público beneficiado e ODS

- **Problema real:** escolas, UBS e famílias na periferia ficam longe das estações oficiais de qualidade do ar e só descobrem a fumaça quando alguém passa mal. Uma prefeitura não quer pagar servidor ligado de madrugada em cada bairro.
- **Cidadão beneficiado:** coordenação de escola e UBS, famílias com crianças, idosos e pessoas com asma, além de vizinhos que enviam relatos de queimada.
- **Métrica medida e limiares de risco** (idênticos ao firmware ESP32 da disciplina 02 e à API da disciplina 05):
  - `gas_voc` (sensor de fumaça e gases): `< 830` = `normal`, `830 a 1139` = `atencao`, `>= 1140` = `critico`
  - `gas_co` (monóxido de carbono): `< 1010` = `normal`, `1010 a 1279` = `atencao`, `>= 1280` = `critico`
- **Conexão com os ODS:** ODS 3 (aviso antes da crise respiratória), ODS 10 (sensor barato onde não há estação oficial) e ODS 11 (dado aberto por bairro com custo proporcional ao uso).

## O que a função faz com cada leitura

1. **Validação estrita (`POST /ocorrencias`):** confere JSON, tipos numéricos finitos, faixas válidas, tamanho do relato (até 500 caracteres) e `medido_em` (ISO 8601). Qualquer erro devolve HTTP `400` e registra `WARNING LEITURA DESCARTADA` no CloudWatch, nunca `500`.
2. **Classificação local de risco:** classifica `normal`, `atencao` ou `critico` pelos limiares acima, independente de rede ou serviço externo.
3. **Camada de IA resiliente (sem segredo no código):**
   - **Caminho escolhido: Hugging Face (`cardiffnlp/twitter-xlm-roberta-base-sentiment`)** via `https://router.huggingface.co/hf-inference/models/{modelo}`, usando apenas `urllib` da biblioteca padrão e token Read na variável de ambiente `HF_TOKEN`.
   - **Por que Hugging Face e não Amazon Comprehend:** testamos `comprehend:DetectSentiment` pela `LabRole` do AWS Academy Learner Lab e o laboratório bloqueia a permissão com `AccessDeniedException`. O código ainda suporta `AI_PROVIDER=comprehend` para contas com a política `ComprehendReadOnly`, mas o padrão é Hugging Face por ser gratuito, entender português informal de relato e não exigir permissão extra de IAM.
   - **Resiliência comprovada na AWS:** com `HF_TOKEN` cadastrado na Lambda (`GET /health` -> `"ia_ativa": true`), cada relato dispara a chamada HTTPS real para `router.huggingface.co`. Quando a cota gratuita mensal de Inference Providers retorna `HTTP 402` (ou em caso de timeout/indisponibilidade), a Lambda registra `WARNING` no CloudWatch (`Hugging Face respondeu 402...`) e conclui normalmente a classificação por limiar e a gravação no RDS PostgreSQL (`HTTP 201`).
4. **Persistência e observabilidade:** grava na tabela `ocorrencias` do RDS usando consultas parametrizadas (`%s` no `pg8000`) com SSL obrigatório e devolve HTTP `201`. Leituras críticas geram `WARNING ALERTA CIDADAO` no CloudWatch.

## Evidências ponta a ponta coletadas na AWS

Todas as evidências estão em `docs/evidencias/` (e incluídas em `deliverables/07-cloud-serverless.zip`):

1. `07_aws_lambda_env.png`: console da Lambda `respiracidadao-central` exibindo todas as variáveis de ambiente (`AI_PROVIDER`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `HF_MODEL`, `HF_API_URL`, `DB_PASSWORD` e `HF_TOKEN`, com ambos os segredos ocultados por segurança).
2. `07_aws_simulador.png`: terminal executando `GET /health` (`ia_ativa: true`), `POST /ocorrencias` inválido (`400`), `simulador_dispositivo.py --cenario normal --lugar ubs`, `--cenario queimada --lugar escola` (escalando até `critico << ALERTA`) e `GET /ocorrencias`.
3. `07_aws_cloudwatch.png`: console do CloudWatch Logs (`/aws/lambda/respiracidadao-central`) mostrando `PAYLOAD RECEBIDO`, chamada HTTPS real à Hugging Face com fallback resiliente (`WARNING Hugging Face respondeu 402`), `CLASSIFICACAO`, `ALERTA CIDADAO` (`WARNING`) e `GRAVADO NO RDS`.
4. `07_aws_rds_console.png` e `07_aws_rds_select.png`: console do RDS `respiracidadao-db` (`Available`, PostgreSQL 18.3, `StorageEncrypted=True`) e consulta `run_sql.py --consultas` exibindo as 15 ocorrências persistidas e agregadas por sensor.

## Como reproduzir

### Teste local (sem AWS)

```bash
python3 teste_local.py                       # 8 verificacoes automatizadas
python3 servidor_local.py                    # simula a Lambda com SQLite
FUNCTION_URL=http://127.0.0.1:8099 python3 simulador_dispositivo.py --cenario queimada
```

### Publicação e validação na AWS

Com credenciais configuradas em `~/.aws/credentials` (AWS Academy Learner Lab ou conta própria):

```bash
DB_PASSWORD='sua-senha-forte' ./deploy_aws.sh
# opcional, para ativar analise de sentimento externa:
# HF_TOKEN='hf_...' DB_PASSWORD='sua-senha-forte' ./deploy_aws.sh
```

Validação direta na Function URL publicada:

```bash
export FUNCTION_URL="https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws"
curl -s "$FUNCTION_URL/health"
python3 simulador_dispositivo.py --url "$FUNCTION_URL" --cenario normal --lugar ubs --leituras 3
python3 simulador_dispositivo.py --url "$FUNCTION_URL" --cenario queimada --lugar escola --leituras 5
curl -s "$FUNCTION_URL/ocorrencias"
DB_HOST="respiracidadao-db.co6giv33mf2r.us-east-1.rds.amazonaws.com" DB_NAME="respiracidadao" DB_USER="respira" DB_PASSWORD="..." python3 run_sql.py --consultas
```

## Escolhas de arquitetura e segurança

- **Lambda fora da VPC:** permite saída direta para a API de IA sem custo fixo de NAT Gateway.
- **Banco com SSL e criptografia em repouso:** o RDS PostgreSQL 18.3 exige SSL (`rds.force_ssl=1`) e roda com disco cifrado (`StorageEncrypted=True`), acessível apenas na porta TCP `5432` pelo Security Group `respiracidadao-db-sg`. Para uso contínuo em produção municipal, banco e Lambda entram juntos em sub-rede privada com VPC Endpoint / NAT.
- **SQL parametrizado:** todas as queries usam placeholders `%s` via `pg8000`, prevenindo SQL Injection.

## Limpeza dos recursos após a avaliação

```bash
aws lambda delete-function --function-name respiracidadao-central
aws rds delete-db-instance --db-instance-identifier respiracidadao-db --skip-final-snapshot
```
