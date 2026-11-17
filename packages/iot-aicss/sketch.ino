/*
 * RespiraCidadao - FIAP GS 2026.2 (02 AICSS)
 * Estacao comunitaria ESP32 para monitoramento de fumaca (MQ-2) e microclima (DHT22).
 *
 * Hardware no Wokwi:
 *   - Sensor 1: Potenciometro simulando modulo MQ-2 no pino GPIO 34 (ADC -> fumaca_ppm 0..400)
 *   - Sensor 2: DHT22 no pino GPIO 15 (temperatura_c e umidade_pct)
 *   - Atuadores: LED Verde (GPIO 26), LED Amarelo (GPIO 27), LED Vermelho (GPIO 14), Buzzer (GPIO 12)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define PIN_MQ2_ADC     34
#define PIN_DHT         15
#define DHTTYPE         DHT22

#define PIN_LED_VERDE   26
#define PIN_LED_AMARELO 27
#define PIN_LED_VERMELHO 14
#define PIN_BUZZER      12

// Limiares locais identicos ao backend Python/Cloud
const float LIMIAR_ATENCAO = 120.0;
const float LIMIAR_CRITICO = 250.0;

// Configuracao de rede (Wokwi-GUEST no simulador Wokwi)
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
// Troque pelo IP/ngrok da API FastAPI ou Function URL da Lambda
const char* API_URL   = "http://host.wokwi.internal:8000/ocorrencias";

const char* DISPOSITIVO_ID = "esp32-respira-01";
const float LATITUDE       = -23.564100;
const float LONGITUDE      = -46.652400;

DHT dht(PIN_DHT, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_AMARELO, OUTPUT);
  pinMode(PIN_LED_VERMELHO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  dht.begin();

  Serial.print("Conectando ao WiFi ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado. IP: " + WiFi.localIP().toString());
}

void acionarAtuadores(const String& status) {
  digitalWrite(PIN_LED_VERDE, status == "normal" ? HIGH : LOW);
  digitalWrite(PIN_LED_AMARELO, status == "atencao" ? HIGH : LOW);
  digitalWrite(PIN_LED_VERMELHO, status == "critico" ? HIGH : LOW);

  if (status == "critico") {
    tone(PIN_BUZZER, 1800, 600);
  } else if (status == "atencao") {
    tone(PIN_BUZZER, 950, 180);
  } else {
    noTone(PIN_BUZZER);
  }
}

String classificarLocal(float fumacaPpm) {
  if (fumacaPpm >= LIMIAR_CRITICO) return "critico";
  if (fumacaPpm >= LIMIAR_ATENCAO) return "atencao";
  return "normal";
}

String relatoPadrao(const String& status) {
  if (status == "critico") return "Fumaca densa detectada pelo no comunitario ESP32";
  if (status == "atencao") return "Elevacao moderada de fumaca e baixa umidade";
  return "Qualidade do ar dentro do limite seguro";
}

void loop() {
  int adc = analogRead(PIN_MQ2_ADC);
  float fumacaPpm = (adc / 4095.0) * 400.0;

  float tempC = dht.readTemperature();
  float umidPct = dht.readHumidity();
  if (isnan(tempC)) tempC = 25.0;
  if (isnan(umidPct)) umidPct = 50.0;

  String status = classificarLocal(fumacaPpm);
  acionarAtuadores(status);

  String json = "{";
  json += "\"dispositivo_id\":\"" + String(DISPOSITIVO_ID) + "\",";
  json += "\"tipo\":\"esp32\",";
  json += "\"latitude\":" + String(LATITUDE, 6) + ",";
  json += "\"longitude\":" + String(LONGITUDE, 6) + ",";
  json += "\"metrica\":\"fumaca_ppm\",";
  json += "\"valor\":" + String(fumacaPpm, 2) + ",";
  json += "\"temperatura_c\":" + String(tempC, 2) + ",";
  json += "\"umidade_pct\":" + String(umidPct, 2) + ",";
  json += "\"relato\":\"" + relatoPadrao(status) + "\"";
  json += "}";

  Serial.println("[ESP32] Status=" + status + " | Payload=" + json);

  if (WiFi.status() != WL_CONNECTED) {
    // Rede caiu: LEDs/buzzer continuam locais; tenta reconectar sem travar o loop.
    Serial.println("[WiFi] desconectado, tentando reconectar...");
    WiFi.reconnect();
  } else {
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(json);
    Serial.println("[HTTP] Resposta status=" + String(code));
    if (code > 0) {
      Serial.println("[HTTP] Corpo=" + http.getString());
    }
    http.end();
  }

  delay(4000);
}
