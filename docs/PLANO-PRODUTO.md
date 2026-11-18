# RespiraCidadão: plano do produto

Documento de trabalho. Atualizado a cada fase; o que está marcado foi feito e verificado.

## A história em uma frase

Uma diretora abre o celular às 7h40 e vê: "Ar ruim perto da escola agora. Mantenha as janelas fechadas e deixe a educação física para depois do almoço."

Tudo no produto existe para essa frase ser verdadeira, rápida e confiável.

## Para quem

- Coordenação de escola e de UBS: decide se a atividade é ao ar livre, se fecha janelas, se avisa pais e pacientes.
- Famílias com criança, idoso ou alguém com asma no bairro: querem saber se é hora de sair.
- Vizinhos: viram fumaça e querem avisar alguém.

## O caminho da informação (sem jargão)

1. Um sensor pequeno na parede da escola mede fumaça, monóxido, temperatura e umidade. Se o ar piora, a luz dele muda de cor na hora, mesmo sem internet.
2. A leitura vai para a central. Lá, um modelo que aprendeu com 6.941 horas de medição real confere a leitura e diz o nível com uma porcentagem de certeza.
3. No app, a pessoa escolhe o lugar e vê a cor, uma frase simples e o que fazer agora.
4. Vizinhos contam o que estão vendo ("cheiro de queimada na praça"). O relato aparece no lugar e a central percebe quando é urgente.
5. O padrão do dia mostra quando o ar costuma estar pior. Na base real, o risco crítico chega a 63% às 19h e fica perto de 20% entre 12h e 16h. Daí sai a dica de horário.
6. Cada registro recebe um selo. Qualquer pessoa confere se alguém mexeu nele depois.

## Regras de voz

- O app não fala de curso, disciplina, grupo, entrega ou nome de modelo. Fala de ar, lugar, horário e ação.
- Números viram frases: "acerta 87 de cada 100 horas", não "F1-macro 0,874".
- Termos técnicos ficam na página "Como funciona", sempre traduzidos.
- Os documentos de entrega levam nomes e RMs só na capa. O resto conta o produto e por que decidimos cada coisa.

## Fases

### 1. Coerência de dados [feito]
- [x] Modelos treinados com as 4 leituras que o sensor mede (antes usavam 11 variáveis de laboratório).
- [x] API grava a leitura com a regra local e o veredito do modelo. 13 testes passando.
- [x] Firmware e circuito do ESP32 no mesmo contrato.

### 2. API de produto
- [ ] Cadastro de lugares (escola, UBS, praça) ligado a cada sensor.
- [ ] `GET /locais`: cada lugar com a última leitura, nível, frase e o que fazer.
- [ ] `POST /relatos` e `GET /relatos`: relato de vizinho, limpo e com urgência detectada.
- [ ] `GET /padrao-horario`: risco por hora do dia, calculado da base real.
- [ ] Testes novos para os três.

### 3. App web reescrito
- [ ] Tela "Agora": seletor de lugar, cartão de status, o que fazer, melhor horário, relatos, últimas leituras.
- [ ] Tela "Como funciona": o caminho da informação, quão confiável é (em frases), "teste uma leitura", privacidade e selo.
- [ ] Modo demonstração discreto para gerar leituras de exemplo.
- [ ] Validar no navegador em desktop e celular. `npm run build` limpo.

### 4. Sensor e nuvem
- [ ] ESP32 no Wokwi com print dos 3 estados.
- [ ] `receiver_csv.py` e `run_3_cenarios.py` no contrato novo.
- [ ] Kit de nuvem: Lambda no contrato novo, script de deploy, SQL, README dizendo o que o Israel precisa fazer.

### 5. Entregas
- [ ] Reescrever os textos de cada entrega na voz do produto, com prints reais e gráficos.
- [ ] Regerar PDF/DOCX, slides e zips. README do repositório com cara de produto.

### 6. Revisão e envio
- [ ] Council (GPT-6.1 Terra high + Gemini 4 Hydrogen high) sobre o projeto inteiro.
- [ ] Corrigir bloqueadores e "should".
- [ ] Commit, push, PR, Drive atualizado, relatório final.

## Decisões registradas

| Decisão | Por quê |
|---|---|
| Modelo usa só o que o sensor mede | Um modelo melhor que depende de equipamento de laboratório não roda em nenhum bairro. Perdemos 1 ponto de acerto. |
| A luz do sensor segue uma regra simples | Precisa funcionar sem internet. A regra acerta 84 de cada 100 horas. |
| A central confere com o modelo | Ganha 3 pontos de acerto sobre a regra e dá uma porcentagem de certeza. |
| Dica de horário vem da base real | 13h a 16h tem menos da metade do risco crítico das 8h e das 19h. |
| Relatos ficam separados das leituras | Relato é opinião de pessoa; leitura é medida. O app mostra os dois lado a lado e não mistura. |
