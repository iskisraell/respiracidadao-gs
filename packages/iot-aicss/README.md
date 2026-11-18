# Sensor do RespiraCidadão (ESP32)

O sensor fica na parede da escola, da UBS ou da praça. Ele mede gases, monóxido de carbono, temperatura e umidade a cada 3 segundos. Acende a luz da cor certa na hora, mesmo sem internet. Quando tem rede, manda a leitura para a central.

```text
gases + monóxido + temperatura + umidade -> ESP32 -> luz e buzzer (na hora, sem rede)
                                                  -> JSON por HTTP -> central (API) -> app
```

## Circuito

| Peça | Pino | Para que serve |
|---|---|---|
| Potenciômetro no lugar do MQ-135 | GPIO 34 | Índice de gases e fumaça (380 a 2250) |
| Potenciômetro no lugar do MQ-7 | GPIO 35 | Índice de monóxido de carbono (640 a 2100) |
| DHT22 | GPIO 15 | Temperatura e umidade |
| LED verde, amarelo, vermelho | GPIO 26, 27, 14 | Ar bom, carregado, ruim |
| Buzzer | GPIO 25 | Bipe curto no amarelo, alarme no vermelho. Ajuda quem não enxerga a luz |

Os índices estão na mesma escala dos sensores da base de 6.941 horas usada para treinar a central. Por isso a central lê o mesmo número que o ESP32 mede.

## A regra da luz

| Índice de gases | Luz | Buzzer |
|---|---|---|
| abaixo de 830 | verde | quieto |
| 830 a 1139 | amarela | bipe curto (950 Hz) |
| 1140 ou mais | vermelha | alarme (1800 Hz) |

Os limites vêm da base real e são os mesmos no firmware, no receptor, na API e na função de nuvem. Sozinha, essa regra acerta 84 de cada 100 horas. A central confere com o modelo e chega a 87.

## Rodando no Wokwi

1. Abra um projeto ESP32 novo em wokwi.com.
2. Cole `sketch.ino` e `diagram.json`. Em Library Manager, adicione `DHT sensor library` e `Adafruit Unified Sensor` (lista em `libraries.txt`).
3. Clique em play e gire o potenciômetro de gases. A luz muda e o Serial Monitor mostra o JSON.

Os prints em `evidencias/` são dessa simulação. Os números abaixo são os que o potenciômetro marcou no print; os cenários de teste (`run_3_cenarios.py`) usam 706/925, 980/1120 e 1280/1383, a uma unidade de distância:

| Nível | Gases | Monóxido | Print |
|---|---|---|---|
| Ar bom | 706 | 926 | `evidencias/wokwi_1_ar_bom.png` |
| Ar carregado | 980 | 1120 | `evidencias/wokwi_2_ar_carregado.png` |
| Ar ruim | 1279 | 1384 | `evidencias/wokwi_3_ar_ruim.png` |

No Wokwi gratuito o ESP32 não alcança a API no seu computador (`host.wokwi.internal` exige o gateway pago). O Serial Monitor mostra `SEM REDE: alerta local ativo`, e é exatamente o comportamento que queremos numa queda de internet: a luz continua funcionando.

## Mandando as 3 leituras sem o hardware

`run_3_cenarios.py` envia o mesmo JSON que o ESP32 manda, um para cada lugar:

```bash
python run_3_cenarios.py                              # para a API (127.0.0.1:8000)
python receiver_csv.py                                # receptor mínimo, grava leituras_iot.csv
python run_3_cenarios.py --url http://127.0.0.1:8085
```

Saída contra a API:

```text
Ar bom na UBS Vila Esperança         gravado nível normal  | central: normal (100%)
Ar carregado na Praça da Sé          gravado nível atencao | central: atencao (95%)
Ar ruim na Escola Jardim Primavera   gravado nível critico | central: critico (93%)
```

## O que é real e o que é simulado

- Real: firmware, circuito, regra da luz, JSON, receptor em Python e gravação em CSV.
- Simulado: os gases vêm de potenciômetros. Um MQ-135 ou MQ-7 de verdade precisa de 24 a 48 horas de aquecimento e calibração contra uma estação de referência antes de dar números confiáveis.
- Sem rede, a leitura daquele momento não é guardada no ESP32. Um próximo passo seria uma fila em memória para mandar depois.
