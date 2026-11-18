#!/usr/bin/env bash
# Publica a central na AWS: banco PostgreSQL (RDS), tabela, função Lambda e o endereço público dela.
#
# Funciona no AWS Academy Learner Lab (usa a role LabRole) e numa conta própria no nível gratuito.
# Antes: `aws configure` (ou cole as credenciais do Learner Lab em ~/.aws/credentials).
#
#   DB_PASSWORD='uma-senha-forte' ./deploy_aws.sh            # cria tudo
#   HF_TOKEN=... DB_PASSWORD=... ./deploy_aws.sh             # com a leitura de relatos por IA
#
# Rodar de novo é seguro: o que já existe é reaproveitado e o código da função é atualizado.
set -euo pipefail

REGIAO="${AWS_REGION:-us-east-1}"
FUNCAO="${FUNCAO:-respiracidadao-central}"
BANCO="${BANCO:-respiracidadao-db}"
DB_NAME="${DB_NAME:-respiracidadao}"
DB_USER="${DB_USER:-respira}"
: "${DB_PASSWORD:?defina DB_PASSWORD (mínimo 8 caracteres)}"
HF_TOKEN="${HF_TOKEN:-}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
export AWS_DEFAULT_REGION="$REGIAO"

passo() { printf '\n== %s\n' "$*"; }

passo "Conta"
CONTA=$(aws sts get-caller-identity --query Account --output text)
echo "conta $CONTA, região $REGIAO"

passo "Banco PostgreSQL ($BANCO)"
if ! aws rds describe-db-instances --db-instance-identifier "$BANCO" >/dev/null 2>&1; then
  VPC=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)
  SG=$(aws ec2 create-security-group --group-name "$BANCO-sg" --description "Postgres do RespiraCidadao" \
        --vpc-id "$VPC" --query GroupId --output text 2>/dev/null \
      || aws ec2 describe-security-groups --filters Name=group-name,Values="$BANCO-sg" --query 'SecurityGroups[0].GroupId' --output text)
  # A Lambda roda fora da VPC, então o banco precisa aceitar conexão pública na 5432.
  # Ambiente de demonstração: depois da apresentação, apague o banco (veja o fim do README).
  aws ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 5432 --cidr 0.0.0.0/0 >/dev/null 2>&1 || true
  aws rds create-db-instance --db-instance-identifier "$BANCO" --engine postgres \
    --db-instance-class db.t3.micro --allocated-storage 20 --db-name "$DB_NAME" \
    --master-username "$DB_USER" --master-user-password "$DB_PASSWORD" \
    --vpc-security-group-ids "$SG" --publicly-accessible --backup-retention-period 0 \
    --no-multi-az >/dev/null
  echo "criando o banco (leva de 5 a 10 minutos)..."
fi
aws rds wait db-instance-available --db-instance-identifier "$BANCO"
DB_HOST=$(aws rds describe-db-instances --db-instance-identifier "$BANCO" --query 'DBInstances[0].Endpoint.Address' --output text)
echo "banco em $DB_HOST"

passo "Tabela"
DB_HOST="$DB_HOST" DB_NAME="$DB_NAME" DB_USER="$DB_USER" DB_PASSWORD="$DB_PASSWORD" \
  python3 "$AQUI/run_sql.py" "$AQUI/tabela_ocorrencias.sql"

passo "Pacote da função"
PACOTE=$(mktemp -d)
python3 -m pip install -q -r "$AQUI/requirements.txt" -t "$PACOTE"
cp "$AQUI/lambda_function.py" "$PACOTE/"
(cd "$PACOTE" && zip -qr "$AQUI/funcao.zip" .)
rm -rf "$PACOTE"

passo "Função Lambda ($FUNCAO)"
AMBIENTE="Variables={DB_HOST=$DB_HOST,DB_PORT=5432,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,HF_TOKEN=$HF_TOKEN}"
if aws lambda get-function --function-name "$FUNCAO" >/dev/null 2>&1; then
  aws lambda update-function-code --function-name "$FUNCAO" --zip-file "fileb://$AQUI/funcao.zip" >/dev/null
  aws lambda wait function-updated --function-name "$FUNCAO"
  aws lambda update-function-configuration --function-name "$FUNCAO" --environment "$AMBIENTE" >/dev/null
else
  ROLE="${LAMBDA_ROLE_ARN:-arn:aws:iam::$CONTA:role/LabRole}"
  aws lambda create-function --function-name "$FUNCAO" --runtime python3.12 \
    --handler lambda_function.lambda_handler --role "$ROLE" --timeout 30 --memory-size 256 \
    --zip-file "fileb://$AQUI/funcao.zip" --environment "$AMBIENTE" >/dev/null
fi
aws lambda wait function-active --function-name "$FUNCAO"

passo "Endereço público"
URL=$(aws lambda get-function-url-config --function-name "$FUNCAO" --query FunctionUrl --output text 2>/dev/null \
  || aws lambda create-function-url-config --function-name "$FUNCAO" --auth-type NONE --query FunctionUrl --output text)
aws lambda add-permission --function-name "$FUNCAO" --statement-id url-publica \
  --action lambda:InvokeFunctionUrl --principal '*' --function-url-auth-type NONE >/dev/null 2>&1 || true
rm -f "$AQUI/funcao.zip"

cat <<FIM

Pronto. A central está em:
  $URL

Teste:
  curl ${URL%/}/health
  FUNCTION_URL=$URL python3 simulador_dispositivo.py --cenario queimada

Logs:   console AWS > CloudWatch > Log groups > /aws/lambda/$FUNCAO
Banco:  DB_HOST=$DB_HOST DB_NAME=$DB_NAME DB_USER=$DB_USER DB_PASSWORD=... python3 run_sql.py --consultas
FIM
