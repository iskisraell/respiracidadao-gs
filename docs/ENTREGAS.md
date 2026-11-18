# Entregas e roteiros dos vídeos

Sala 1TIAPZ1, grupo Perceptron:

- Giovanni Henrique Pereira Hessel (RM 570574)
- Suellen Pereira da Silva (RM 573862)
- Israel Carneiro de Toledo (RM 573854)

Prazo: 19/11/2026 às 23:55. Mandem até as 17h para ter folga se o portal travar.

## O que vai em cada portal

| Entrega | Como enviar | Arquivos |
|---|---|---|
| 01 AI Challenges | Link do YouTube (não listado) | Vídeo de até 7 min. O PDF `01_...Dossie_Integrador` serve de roteiro visual. |
| 02 AICSS | Upload de `deliverables/02-aicss-iot.zip` | PDF, `sketch.ino`, `diagram.json`, `libraries.txt`, `receiver_csv.py`, `run_3_cenarios.py`, prints do Wokwi. Capa com RMs já está no PDF. |
| 03 Cybersecurity | PDF + link do vídeo | `03_...Cybersecurity.pdf` (4 páginas) e pitch de até 5 min. |
| 04 Data Science | **Individual**, SurveyMonkey | Cada um roda o `CRIACAO_CARGA_ORACLE.sql`, confere os nomes das colunas e cola as 5 consultas de `packages/data-science-oracle`. Nada no portal. |
| 05 Python | Upload de `deliverables/05-computational-thinking-python.zip` | PDF, código da central e testes. |
| 06 ML | Upload do zip + link do vídeo | Notebook, slides `.pptx`, resumo em PDF, gráficos. Pitch de até 5 min. |
| 07 Cloud | Portal: zip, URL da função, endpoint do RDS, 4 prints, vídeo | Depende do deploy na AWS. Ver abaixo. |
| 08 Redes Neurais | Upload do zip + link do vídeo | Notebook com as 8 etapas, PDF, gráficos. |
| 09 Estatística | **Upload direto dos 3 arquivos, sem link e sem zip** | `air_quality_clean.csv`, `analise_estatistica.py`, `09_...Relatorio_Estatistico.pdf`. Cadastro errado custa 2 pontos. |

Antes de gravar qualquer vídeo: YouTube não listado (teste o link numa aba anônima), rosto de quem fala aparecendo, sem música, e uma tela com os três nomes e RMs no começo ou no fim.

## Antes de gravar: subir o produto

```bash
.venv/bin/uvicorn app.main:app --app-dir apps/api --port 8000
cd apps/web && npm run dev
```

Abra http://localhost:5173. Se a lista de lugares estiver vazia, clique em "Modo demonstração" no rodapé e gere as leituras de exemplo.

## 01: vídeo integrador (até 7 min)

1. **0:00 a 0:50, a cena.** Leia a frase da diretora às 7h40. Diga para quem é: coordenação de escola e UBS, famílias com criança, idoso ou alguém com asma, e o vizinho que viu fumaça. ODS 3, 10 e 11. Cite uma ideia concreta de um convidado da live de lançamento e o que ela mudou no produto. **Israel: preencha com o que vocês anotaram da live; o PDF só traz o tema CitizenTech, e o professor pede a ideia do convidado.**
2. **0:50 a 2:00, o caminho de uma leitura.** Mostre o diagrama `docs/assets/arquitetura_uml_respiracidadao.png` e depois o de sequência `docs/assets/uml_sequencia_leitura.png` (foi com ele que vocês fecharam o JSON entre sensor, central e app) e conte em uma frase o papel de cada parte: sensor (02), central (05), nuvem (07), proteções (03), modelo (06), segunda opinião (08), estatística (09).
3. **2:00 a 5:00, demonstração.**
   - Tela Agora: clique na Escola Jardim Primavera (vermelha). Leia "Ar ruim agora", o que fazer e a linha "A central conferiu e concorda: Ruim, com 93% de confiança".
   - Mostre o melhor horário (14h às 17h) e explique que vem de 6.941 horas reais.
   - Escreva um relato ("cheiro de queimada no portão") e mostre ele aparecer marcado como urgente.
   - Tela Como funciona: mexa nos controles de "Teste uma leitura" até virar vermelho e mostre a central e a segunda opinião concordando.
   - Mostre um print do Wokwi com o LED vermelho (`packages/iot-aicss/evidencias`).
4. **5:00 a 5:40, gestão.** Três frentes (sensor e nuvem; estatística e modelos; central, app e proteções) presas ao mesmo contrato JSON e a um plano único no repositório. Conte as duas dificuldades: trocar 11 medidas de laboratório pelas 4 do ESP32 e o Wokwi gratuito sem rede externa (viraram luz local + receptor Python).
5. **5:40 a 6:40, o que é real e o que vem depois.** Real: sensor no simulador, central, modelos, app. Depois: placa física, publicação na nuvem, recalibração com estação CETESB, aviso no WhatsApp. Feche com acessibilidade (cor sempre com palavra, alarme sonoro), dados pessoais (relato sem nome) e a tela de RMs.

## Pitches curtos (até 5 min cada)

**03 Cybersecurity.** Mostre as 5 camadas e a matriz de 6 riscos do PDF. Ao vivo, com a central rodando:

```bash
.venv/bin/pytest apps/api/tests -q        # 16 testes, cada proteção tem o seu
for i in $(seq 1 32); do curl -s -o /dev/null -w "%{http_code} " -X POST localhost:8000/relatos \
  -H 'Content-Type: application/json' -d '{"local_id":"praca-da-se","texto":"teste"}'; done   # termina em 429
curl -s -X DELETE localhost:8000/ocorrencias -w "\n%{http_code}\n"   # 401 sem chave
curl -s localhost:8000/security/verify/1                              # integro: true
```

Feche com o cenário da mensagem falsa da "Defesa Civil" no WhatsApp da diretora e as respostas de LGPD.

**06 Machine Learning.** Use os slides `docs/06_RespiraCidadao_ML_Slides.pptx`. O ponto central é o slide "Por que o modelo usa só o que o sensor mede": 84 com a regra, 87 com as 4 medidas, 88 com laboratório que nenhum bairro tem. Termine com o teste de uma leitura na tela Como funciona.

**07 Cloud.** Só dá para gravar depois do deploy. Mostre `simulador_dispositivo.py --cenario queimada --lugar escola` enviando para a URL da função, os avisos no CloudWatch e o `python run_sql.py --consultas` listando as leituras no RDS. Os 4 prints saem dessa mesma sessão.

**08 Redes Neurais.** Percorra as 8 etapas no notebook `respira_neural_network.ipynb`. Mostre a rede A decorando (5,2 pontos entre treino e teste) e a B regularizada com 1,1 ponto. Termine com o card "Segunda opinião" no app.

## 07: o que precisa da AWS

Dá para mostrar tudo localmente (`servidor_local.py` e `teste_local.py`), mas o enunciado pede URL da função, endpoint do RDS e prints do console. Para isso:

1. Pegue uma conta: AWS Academy Learner Lab (se a FIAP liberou) ou conta própria no nível gratuito.
2. Com as credenciais configuradas, rode `bash packages/cloud-serverless/deploy_aws.sh`. Ele cria o banco, a tabela e a função, e imprime a URL e os comandos de teste.
3. Tire os 4 prints: variáveis de ambiente da função, simulador enviando, CloudWatch, SELECT no banco.
4. Ao terminar, apague os recursos com os comandos do fim do README da pasta para não gerar cobrança.
