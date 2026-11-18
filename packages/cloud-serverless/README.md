# Central do RespiraCidadão na nuvem (AWS)

A central é quem recebe a leitura do sensor, decide o nível e guarda o histórico. No dia a dia ela roda como a API do repositório (`apps/api`). Esta pasta é a mesma central em formato de nuvem, para funcionar sem um servidor ligado o tempo todo:

```text
sensor ESP32 --HTTPS--> Lambda (Function URL) --> PostgreSQL no RDS
                              |--> CloudWatch: cada leitura, cada alerta, cada erro
                              '--> IA de texto (Hugging Face): lê o relato, se vier um
```

## Para quem

Uma prefeitura não quer pagar servidor ligado de madrugada em cada bairro. Com a central na nuvem, a família consulta o mesmo nível que a escola vê, e a conta só corre quando chega leitura. ODS 3 (aviso antes da crise respiratória), ODS 10 (sensor barato onde não há estação oficial) e ODS 11 (dado aberto por bairro).

## O que a função faz com cada leitura

1. Confere o JSON. Campo faltando, número inválido ou tipo desconhecido vira resposta 400 e um aviso no log. Nunca 500.
2. Classifica pelo índice de gases, com os mesmos limites do sensor: abaixo de 830 é ar bom, de 830 a 1139 é ar carregado, 1140 ou mais é ar ruim.
3. Se a leitura trouxer um relato ("fumaça no portão, crianças tossindo"), manda o texto para um modelo de sentimento em português. Se a IA cair ou demorar, a leitura é gravada do mesmo jeito.
4. Grava no PostgreSQL e devolve o nível. Ar ruim gera um `ALERTA CIDADAO` no CloudWatch.

## Precisa de conta na AWS?

Para mostrar funcionando, não. Tudo roda no seu computador:

```bash
python3 teste_local.py                       # 8 verificações, sem banco e sem internet
python3 servidor_local.py                    # a função com SQLite no lugar do RDS
FUNCTION_URL=http://127.0.0.1:8099 python3 simulador_dispositivo.py --cenario queimada
```

Para publicar de verdade, sim. Duas opções gratuitas:

| Opção | O que é | Custo |
|---|---|---|
| AWS Academy Learner Lab | Laboratório que a faculdade libera. Já vem com a role `LabRole`, que o script usa | Zero. Os créditos são do laboratório |
| Conta própria | Conta nova na AWS, com cartão | Lambda e CloudWatch ficam no nível gratuito. O RDS `db.t3.micro` entra no plano gratuito de conta nova; apague no fim para não gastar |

## Publicando (um comando)

Requisitos: AWS CLI configurada (`aws configure`, ou as credenciais do Learner Lab em `~/.aws/credentials`), Python 3 e `zip`.

```bash
DB_PASSWORD='escolha-uma-senha' ./deploy_aws.sh
# opcional, para a IA ler os relatos: HF_TOKEN=<token de leitura do Hugging Face>
```

O script cria o banco (5 a 10 minutos), a tabela, a função e o endereço público, e no fim imprime a URL e os comandos de teste. Rodar de novo só atualiza o código.

Fora do Learner Lab, crie antes uma role com a política `AWSLambdaBasicExecutionRole` e passe `LAMBDA_ROLE_ARN=arn:aws:iam::<conta>:role/<nome>`.

## As 4 telas que provam que funciona

1. Lambda > Configuração > Variáveis de ambiente (com a senha e o token ocultos).
2. Terminal com `simulador_dispositivo.py --cenario queimada` subindo até `critico << ALERTA`.
3. CloudWatch com `PAYLOAD RECEBIDO`, `CLASSIFICACAO` e `ALERTA CIDADAO`.
4. `python3 run_sql.py --consultas` mostrando as leituras gravadas no RDS.

## Escolhas e limites

- A função fica fora da rede privada da AWS (VPC). Lá dentro, para chegar à IA na internet, ela precisaria de um NAT Gateway, que cobra por hora mesmo parado. O preço é o banco aceitar conexão pública na porta 5432, protegido por senha e SSL. Serve para demonstração. Em produção, o banco ficaria numa sub-rede privada.
- A conexão com o banco usa SSL, porque o RDS com PostgreSQL 15 ou mais novo recusa conexão sem ele.
- O caminho do banco foi testado num PostgreSQL local: tabela criada, leituras gravadas e consultadas. O `deploy_aws.sh` não foi executado numa conta real, porque não temos credenciais aqui.
- Usamos a Hugging Face e não o Amazon Comprehend porque o token é gratuito, não exige permissão extra de IAM (o Learner Lab bloqueia várias) e o modelo `cardiffnlp/twitter-xlm-roberta-base-sentiment` entende português informal.
- A IA de relatos é opcional. Sem `HF_TOKEN`, a função grava tudo e deixa o sentimento vazio.

## Apagando tudo depois

```bash
aws lambda delete-function --function-name respiracidadao-central
aws rds delete-db-instance --db-instance-identifier respiracidadao-db --skip-final-snapshot
```
