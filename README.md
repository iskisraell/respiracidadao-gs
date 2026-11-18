# RespiraCidadão

Uma diretora abre o celular às 7h40 e lê: "Ar ruim perto da escola agora. Mantenha as janelas fechadas e deixe a educação física para depois do almoço."

O RespiraCidadão avisa escolas, UBS e famílias quando o ar perto delas piora. Um sensor barato na parede mede o ar e acende uma luz na hora, mesmo sem internet. A central confere a leitura com um modelo treinado em 6.941 horas de medição real. O app mostra a cor, uma frase e o que fazer.

![Tela Agora](docs/assets/app_agora.png)

## O que tem aqui

| Pasta | O que é |
|---|---|
| `apps/web` | O app (React + TypeScript). Telas "Agora" e "Como funciona". |
| `apps/api` | A central (FastAPI). Recebe leituras, decide o nível, guarda em CSV e SQLite, serve o app. |
| `packages/iot-aicss` | O sensor: firmware ESP32, circuito Wokwi, receptor em Python e prints dos 3 estados. |
| `packages/cloud-serverless` | A central na nuvem: função AWS Lambda, tabela PostgreSQL e um script que publica tudo. |
| `packages/ml-modelling` | Como o modelo da central foi escolhido (notebook com 6 modelos comparados). |
| `packages/neural-networks` | A segunda opinião: rede neural em PyTorch. |
| `packages/stats-r-python` | A estatística que mostra que o sensor barato explica o monóxido real. |
| `data` | Base real UCI Air Quality, bruta e limpa. |
| `docs` | Plano do produto, documentos de entrega e o diagrama do caminho da informação. |

## Rodar no seu computador

```bash
# Central (porta 8000)
python -m venv .venv && .venv/bin/pip install -e apps/api
export RESPIRA_API_KEY="uma-chave-local"   # só para apagar dados; sem ela a rota fica fechada
.venv/bin/uvicorn app.main:app --app-dir apps/api --port 8000

# App (porta 5173), em outro terminal
cd apps/web && npm install && npm run dev
```

Abra http://localhost:5173. Para ver os três níveis sem sensor, use "Modo demonstração" no rodapé ou rode `python packages/iot-aicss/run_3_cenarios.py`.

## Testes

```bash
.venv/bin/pip install pytest httpx
.venv/bin/pytest apps/api/tests                       # 16 testes da central
.venv/bin/python packages/cloud-serverless/teste_local.py   # 8 verificações da função na nuvem
```

## Quanto dá para confiar

- A luz do sensor segue uma regra simples e acerta 84 de cada 100 horas.
- A central acerta 87 de cada 100 com as quatro medidas do sensor. Nenhuma hora de ar bom virou ar ruim no teste, nem o contrário.
- A base é de uma cidade italiana. Em cada bairro novo o sensor precisa de algumas semanas ao lado de uma estação oficial para recalibrar.

As decisões e o motivo de cada uma estão em [docs/PLANO-PRODUTO.md](docs/PLANO-PRODUTO.md). O material de entrega por disciplina está em [docs/ENTREGAS.md](docs/ENTREGAS.md).
