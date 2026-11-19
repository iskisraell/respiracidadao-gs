# Entregas e roteiros dos vídeos

Sala 1TIAPZ1, grupo Perceptron:

- Giovanni Henrique Pereira Hessel, RM 570574
- Suellen Pereira da Silva, RM 573862
- Israel Carneiro de Toledo, RM 573854

Prazo final: 19/11/2026 às 23h55. A recomendação é subir tudo até as 17h para ter margem caso o portal fique lento.

## O que vai em cada disciplina

| Entrega | Como enviar | Arquivos prontos |
|---|---|---|
| 01 AI Challenges | Link do YouTube não listado | Vídeo de até 7 min. Roteiro de narração para a Suellen em `docs/01-ai-challenges/01_RespiraCidadao_Roteiro_Narracao_AIC.pdf` e dossiê integrador em `01_...Dossie_Integrador.pdf`. |
| 02 AICSS | Upload de `deliverables/02-aicss-iot.zip` | PDF com capa e RMs, código do ESP32, diagrama do circuito, lista de bibliotecas, receptor CSV, simulador de 3 cenários e capturas do Wokwi. |
| 03 Cybersecurity | PDF e link do vídeo | `03_...Cybersecurity.pdf` com controles locais e validações reais na AWS, mais vídeo de até 5 min. |
| 04 Data Science | Individual no SurveyMonkey | Cada integrante executa `CRIACAO_CARGA_ORACLE.sql`, confere as colunas e responde as 5 consultas de `packages/data-science-oracle`. Não vai arquivo no portal. |
| 05 Python | Upload de `deliverables/05-computational-thinking-python.zip` | PDF, código completo da central em Python e os 24 testes automáticos. |
| 06 Machine Learning | Upload do zip e link do vídeo | Notebook completo, apresentação `.pptx`, relatório em PDF e gráficos. Vídeo de até 5 min. |
| 07 Cloud | Zip, URL da Lambda, endpoint do RDS, 5 prints e vídeo | Ambiente publicado e validado na AWS, região `us-east-1`. O arquivo `07-cloud-serverless.zip` já reúne os 5 prints reais da AWS, PDF, SQL, código da Lambda e README. Falta apenas gravar o vídeo de até 5 min. |
| 08 Redes Neurais | Upload do zip e link do vídeo | Notebook com as 8 etapas obrigatórias, relatório em PDF e gráficos. Vídeo de até 5 min. |
| 09 Estatística | Upload dos 3 arquivos soltos, sem zip e sem link | `air_quality_clean.csv`, `analise_estatistica.py` e `09_...Relatorio_Estatistico.pdf`. Enviar fora desse formato desconta 2 pontos. |

Antes de gravar qualquer vídeo, confira quatro regras simples: publique como não listado no YouTube e teste o link em aba anônima, mantenha o rosto de quem fala visível na tela, grave sem música de fundo e mostre uma tela com os três nomes e RMs no início ou no final.

## Antes de gravar: subir o produto localmente

```bash
.venv/bin/uvicorn app.main:app --app-dir apps/api --port 8000
cd apps/web && npm run dev
```

Abra `http://localhost:5173`. Se a lista de lugares abrir vazia, clique em "Modo demonstração" no rodapé para gerar as leituras de exemplo.

## 01: vídeo integrador, até 7 minutos

1. **0:00 a 0:50, a cena inicial.** Leia o aviso da diretora às 7h40. Diga quem usa o sistema: escolas, postos de saúde, famílias com crianças, idosos, pessoas com asma e vizinhos que percebem fumaça. Conecte aos ODS 3, 10 e 11 e cite uma ideia concreta da aula inaugural de tecnologia cidadã que influenciou o projeto. **Atenção, Israel:** preencha essa referência com a fala exata do convidado da live que o grupo anotou, pois o professor cobra essa citação.
2. **0:50 a 2:00, o caminho de uma leitura.** Mostre o diagrama geral em `docs/assets/arquitetura_uml_respiracidadao.png` e o diagrama de sequência em `docs/assets/uml_sequencia_leitura.png`. Explique em uma frase o papel de cada matéria: o sensor de IoT mede e dispara o alarme local; Estatística validou os limites com quase 7 mil horas reais; Python centraliza e valida os dados; Cloud roda a mesma central sob demanda na AWS com banco PostgreSQL; Machine Learning e Redes Neurais dão a classificação e a segunda opinião; Cibersegurança protege todo o trajeto.
3. **2:00 a 5:00, demonstração ao vivo.**
   - Na tela Agora, selecione a Escola Jardim Primavera em alerta vermelho. Leia a orientação principal e a confirmação da central com 93% de confiança.
   - Mostre o bloco de melhor horário, das 14h às 17h, explicando que vem das 6.941 horas reais.
   - Envie um relato de morador avisando sobre cheiro de queimada no portão e mostre ele aparecer marcado como urgente.
   - Na aba Como funciona, teste os controles deslizantes até o alerta ficar vermelho e mostre sensor, modelo principal e rede neural concordando.
   - Mostre o print do simulador com LED vermelho aceso em `packages/iot-aicss/evidencias` e os prints reais da AWS em `docs/evidencias/07_aws_*.png`.
4. **5:00 a 5:40, divisão do time e escolhas técnicas.** Explique as três frentes trabalhando sobre o mesmo contrato de dados: sensor e nuvem; estatística e IA; central em Python, app e segurança. Conte as decisões que deixaram o sistema realista: usar só as 4 medidas do sensor barato em vez de 11 de laboratório, manter o alerta local funcionando sem internet no simulador gratuito e trocar o Amazon Comprehend bloqueado no laboratório estudantil por Hugging Face com plano de contingência.
5. **5:40 a 6:40, o que já roda e o que vem depois.** Diferencie o que já está pronto hoje, incluindo a nuvem real na AWS, do que fica para a próxima fase: placa física com bateria solar, calibração ao lado de uma estação da CETESB e alertas no WhatsApp. Feche destacando acessibilidade, privacidade de relatos anônimos e a tela final com nomes e RMs.

## Pitches curtos, até 5 minutos cada

### 03 Cybersecurity

Apresente as cinco camadas de defesa, a matriz de seis riscos e os controles reais na AWS, com banco cifrado, conexão segura e segredos fora do código. Com a central local rodando, mostre os testes ao vivo:

```bash
.venv/bin/pytest apps/api/tests -q
for i in $(seq 1 32); do curl -s -o /dev/null -w "%{http_code} " -X POST localhost:8000/relatos \
  -H 'Content-Type: application/json' -d '{"local_id":"praca-da-se","texto":"teste"}'; done
curl -s -X DELETE localhost:8000/ocorrencias -w "\n%{http_code}\n"
curl -s localhost:8000/security/verify/1
```

A sequência acima prova o limite de envios terminando em erro 429, a recusa de exclusão sem chave com erro 401 e o selo digital íntegro. Feche comentando o golpe da mensagem falsa de "Defesa Civil" no WhatsApp e os cuidados de LGPD.

### 06 Machine Learning

Apresente os slides de `docs/06_RespiraCidadao_ML_Slides.pptx`. O ponto central é comparar os três níveis de acerto: 84% com a regra fixa do sensor, 87% com o modelo usando só as quatro medidas baratas e 88% com onze medidas de laboratório que nenhum bairro tem. Feche simulando uma leitura ao vivo na tela Como funciona do aplicativo.

### 07 Cloud, ambiente AWS pronto para gravar

- **URL pública da Lambda:** `https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws/`
- **Endpoint do RDS PostgreSQL 18.3:** `respiracidadao-db.co6giv33mf2r.us-east-1.rds.amazonaws.com`, porta `5432`, banco `respiracidadao`
- **Logs no CloudWatch:** `/aws/lambda/respiracidadao-central`
- **Evidências já salvas em `docs/evidencias/` e empacotadas no ZIP:** `07_aws_lambda_env.png`, `07_aws_simulador.png`, `07_aws_cloudwatch.png`, `07_aws_rds_console.png` e `07_aws_rds_select.png`.

Comandos para a demonstração ao vivo:

```bash
export FUNCTION_URL="https://6diultpyclfbww5yyqt2oki7bi0ipglh.lambda-url.us-east-1.on.aws"
.venv/bin/python packages/cloud-serverless/simulador_dispositivo.py --cenario normal --lugar ubs --leituras 3 --intervalo 1
.venv/bin/python packages/cloud-serverless/simulador_dispositivo.py --cenario queimada --lugar escola --leituras 5 --intervalo 1
# Mostrar os logs em /aws/lambda/respiracidadao-central no console AWS CloudWatch
# Consultar as tabelas no RDS PostgreSQL com DB_HOST, DB_USER, DB_PASSWORD e DB_NAME exportados:
.venv/bin/python packages/cloud-serverless/run_sql.py --consultas
```

Nota sobre a análise de texto na AWS: o token da Hugging Face já está ativo na Lambda e o endpoint de saúde mostra a IA ligada. Como a conta gratuita atingiu a cota mensal da Hugging Face, a chamada retorna erro 402 e dispara nossa rotina de contingência no CloudWatch, provando que o sistema continua gravando normalmente no PostgreSQL mesmo quando a IA externa falha. Se quiser exibir o sentimento positivo ou negativo ao vivo na gravação, basta substituir o valor de `HF_TOKEN` na Lambda por um token com cota disponível, sem alterar o código.

### 08 Redes Neurais

Percorra as oito etapas do notebook `respira_neural_network.ipynb`. Mostre a rede simples decorando o treino com diferença de 5,2 pontos percentuais e a rede regularizada reduzindo essa diferença para 1,1 ponto. Termine mostrando o cartão de segunda opinião rodando dentro do aplicativo.

## Limpeza da AWS após gravar

Os recursos na AWS ficaram ligados para facilitar a gravação do vídeo de Cloud. Depois de gravar, encerre a Lambda e o banco com os dois comandos do final de `packages/cloud-serverless/README.md` para evitar consumo desnecessário de créditos.
