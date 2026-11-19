# Central do RespiraCidadão na nuvem AWS

A central recebe cada leitura do sensor, decide o nível de risco do ar, grava logs de auditoria no CloudWatch, consulta uma IA para analisar relatos de moradores e salva o histórico no PostgreSQL. No ambiente local, esse trabalho roda na API de `apps/api`. Esta pasta entrega a mesma central em arquitetura serverless na AWS, rodando sob demanda sem manter servidor ligado o tempo todo.

```text
Sensor ou simulador --HTTPS--> AWS Lambda --> Amazon RDS PostgreSQL 18.3 com SSL e disco cifrado
                                  |--> CloudWatch Logs: entrada, validação, classificação, alertas e gravação
                                  '--> IA de texto na Hugging Face: lê o relato sem travar a gravação
```

## Ambiente publicado e validado na AWS, região us-east-1

- **Endereço público da Lambda `respiracidadao-central`:** `https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws/`
- **Banco gerenciado Amazon RDS PostgreSQL 18.3:** `respiracidadao-db.co6giv33mf2r.us-east-1.rds.amazonaws.com`, porta `5432`, banco `respiracidadao`, usuário `respira`, conexão segura obrigatória e armazenamento cifrado. A senha fica apenas na variável de ambiente da Lambda, fora do código.
- **Grupo de logs no CloudWatch:** `/aws/lambda/respiracidadao-central`
- **Configuração da função:** Python 3.12, 256 MB de memória, limite de 30 segundos por execução, rodando fora de rede privada para acessar a API externa de IA sem o custo fixo de um NAT Gateway.

## Problema cidadão, público atendido e ODS

Escolas públicas, postos de saúde e famílias da periferia ficam longe das estações oficiais de qualidade do ar e só percebem uma queimada quando alguém passa mal. Ao mesmo tempo, uma prefeitura ou escola não quer pagar por um servidor ligado de madrugada em cada bairro.

O sistema atende coordenações de escolas e UBS, famílias com crianças, idosos, pessoas com asma e moradores que relatam fumaça perto de casa. Isso se conecta diretamente a três objetivos da ONU: ODS 3 de saúde, ao avisar antes da crise respiratória; ODS 10 de redução das desigualdades, ao levar monitoramento barato onde não há estação oficial; e ODS 11 de cidades sustentáveis, com dados abertos por bairro e custo proporcional ao uso.

### Faixas de risco usadas na classificação

Os limites seguem exatamente o firmware do sensor e a API local:

- Sensor de fumaça e gases, `gas_voc`: abaixo de `830` indica ar normal; de `830` a `1139` indica atenção; a partir de `1140` indica situação crítica.
- Sensor de monóxido de carbono, `gas_co`: abaixo de `1010` indica ar normal; de `1010` a `1279` indica atenção; a partir de `1280` indica situação crítica.

## O que a função faz com cada leitura

1. **Validação na entrada.** Ao receber um envio em `POST /ocorrencias`, a função confere o formato JSON, verifica se os números são válidos e finitos, valida o limite de 500 caracteres para relatos e checa a data da medição. Se algo estiver errado, devolve erro 400 e grava um aviso no CloudWatch, sem derrubar a função.
2. **Classificação local de risco.** Os limiares acima classificam a leitura em normal, atenção ou crítico dentro da própria Lambda, sem depender de serviço externo.
3. **Análise de relatos com plano de contingência.** O texto de relatos passa pelo modelo multilíngue `cardiffnlp/twitter-xlm-roberta-base-sentiment`, acessado via roteador da Hugging Face usando apenas a biblioteca padrão `urllib` do Python e a variável de ambiente `HF_TOKEN`. Testamos antes o Amazon Comprehend, mas o laboratório AWS Academy bloqueia essa permissão na conta estudantil. O código continua pronto para usar Comprehend caso a conta tenha essa permissão liberada. Na nuvem, validamos o fluxo completo com `HF_TOKEN` ativo: quando a cota gratuita mensal da Hugging Face responde com erro 402 ou o serviço fica fora do ar, a Lambda registra um aviso no CloudWatch e conclui normalmente a gravação da leitura no PostgreSQL com resposta 201.
4. **Gravação segura e monitoramento.** Todas as consultas SQL usam parâmetros separados para evitar injeção de código e trafegam por conexão cifrada. Toda leitura crítica grava um alerta específico no CloudWatch para facilitar auditoria.

## Evidências coletadas na AWS

Os cinco registros visuais do ambiente publicado estão em `docs/evidencias/` e empacotados em `deliverables/07-cloud-serverless.zip`:

1. `07_aws_lambda_env.png`: painel da Lambda mostrando todas as variáveis de ambiente configuradas, com a senha do banco e o token da Hugging Face ocultados.
2. `07_aws_simulador.png`: terminal executando a checagem de saúde com IA ativa, um teste de erro 400 proposital, o simulador em cenário normal na UBS, o cenário de queimada na escola até o nível crítico e a consulta das ocorrências gravadas.
3. `07_aws_cloudwatch.png`: logs reais no CloudWatch exibindo a leitura recebida, a chamada externa para a Hugging Face com contingência registrada, a classificação de risco, o alerta cidadão e a confirmação de gravação no RDS.
4. `07_aws_rds_console.png` e `07_aws_rds_select.png`: painel do banco PostgreSQL 18.3 ativo e cifrado na AWS e a consulta direta retornando as 15 ocorrências persistidas e resumidas por sensor.

## Como testar

### Teste local, sem conta na AWS

```bash
python3 teste_local.py
python3 servidor_local.py
FUNCTION_URL=http://127.0.0.1:8099 python3 simulador_dispositivo.py --cenario queimada
```

### Publicação e validação na AWS

Com as credenciais da AWS configuradas em `~/.aws/credentials`:

```bash
DB_PASSWORD='sua-senha-forte' ./deploy_aws.sh
# Para ativar tambem a chamada externa de analise de relatos:
# HF_TOKEN='hf_...' DB_PASSWORD='sua-senha-forte' ./deploy_aws.sh
```

Validação direta na função publicada:

```bash
export FUNCTION_URL="https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws"
curl -s "$FUNCTION_URL/health"
python3 simulador_dispositivo.py --url "$FUNCTION_URL" --cenario normal --lugar ubs --leituras 3
python3 simulador_dispositivo.py --url "$FUNCTION_URL" --cenario queimada --lugar escola --leituras 5
curl -s "$FUNCTION_URL/ocorrencias"
DB_HOST="respiracidadao-db.co6giv33mf2r.us-east-1.rds.amazonaws.com" DB_NAME="respiracidadao" DB_USER="respira" DB_PASSWORD="..." python3 run_sql.py --consultas
```

## Escolhas de arquitetura e segurança

Deixamos a Lambda fora da rede privada para permitir saída direta até a API de IA sem pagar o custo fixo de um NAT Gateway no ambiente estudantil. O banco compensa essa exposição exigindo conexão cifrada obrigatória, disco criptografado, senha isolada em variável de ambiente e acesso restrito à porta 5432 pelo grupo de segurança do banco. Em implantação definitiva numa prefeitura, tanto a função quanto o banco passariam para sub-redes privadas.

## Limpeza dos recursos após a avaliação

```bash
aws lambda delete-function --function-name respiracidadao-central
aws rds delete-db-instance --db-instance-identifier respiracidadao-db --skip-final-snapshot
```
