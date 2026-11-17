# RespiraCidadão — Módulo IoT (`02 - AI Computer Systems & Sensors`)

## Fluxo Funcional

```text
Fumaça / Temperatura / Umidade ─► ESP32 (MQ-2 ADC + DHT22) ─► LEDs + Buzzer ─► JSON HTTP POST ─► API Python ─► CSV + SQLite
```

## Sensores e Atuadores

| Componente | Pino ESP32 | Função no Problema CitizenTech |
|---|---|---|
| Sensor de Gás/Fumaça (MQ-2 simulado por potenciômetro ADC) | `GPIO 34` | Mede concentração de fumaça/compostos combustíveis (`0` a `400 ppm`). |
| Sensor Microclimático `DHT22` | `GPIO 15` | Mede temperatura (`°C`) e umidade relativa (`%`), fatores que agravam dispersão de fumaça e risco respiratório. |
| LED Verde / Amarelo / Vermelho | `GPIO 26 / 27 / 14` | Sinalização visual imediata para cidadãos próximos ao ponto comunitário. |
| Buzzer Piezoelétrico | `GPIO 12` | Alerta sonoro para acessibilidade de pessoas com deficiência visual. |

## Como Simular no Wokwi

1. Crie um projeto **ESP32** no Wokwi e cole `sketch.ino`, `diagram.json` e `libraries.txt` (`DHT sensor library` + `Adafruit Unified Sensor`).
2. O `API_URL` padrão (`host.wokwi.internal:8000`) exige o **Wokwi Private Gateway**; sem ele, exponha a API com um túnel (ngrok / `tailscale serve`) e troque a URL no sketch.
3. Sem rede, rode `python run_3_cenarios.py --url http://127.0.0.1:8000` (API FastAPI) ou `--url http://127.0.0.1:8085` (`receiver_csv.py`) para demonstrar os 3 comportamentos e gerar o CSV.
4. Os limiares `120 / 250 ppm` são os mesmos do sketch, de `receiver_csv.py`, da API e da Lambda.

## O que foi Implementado vs. Simulado

- **Implementado:** firmware `sketch.ino` em C++/Arduino, circuito Wokwi `diagram.json`, regras determinísticas de limiar (`< 120` Normal, `120–249.9` Atenção, `>= 250` Crítico), envio JSON via `HTTPClient`, recepção em Python (`apps/api` e `receiver_csv.py`) com gravação em CSV.
- **Simulado:** variação química de fumaça via potenciômetro no Wokwi e envio automatizado dos 3 cenários via `run_3_cenarios.py`.
- **Limitações:** sensor MQ-2 exige calibração física por curva de resistência (`Rs/R0`) em hardware real e depende de conectividade Wi-Fi local; sem conectividade, apenas o alerta sonoro/visual local permanece ativo.

## ODS Relacionados

- **ODS 3 (Saúde e Bem-Estar):** prevenção de crises respiratórias em escolas e UBS por aviso precoce local e digital.
- **ODS 11 (Cidades e Comunidades Sustentáveis):** monitoramento comunitário de baixo custo contra fumaça urbana e queimadas.
