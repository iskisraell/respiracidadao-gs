/*
 * RespiraCidadao - sensor comunitario ESP32
 *
 * Sensores:
 *   GPIO 34  potenciometro no lugar do MQ-135 (gases/fumaca, indice 380..2250)
 *   GPIO 35  potenciometro no lugar do MQ-7   (monoxido de carbono, indice 640..2100)
 *   GPIO 15  DHT22 (temperatura e umidade)
 * Atuadores:
 *   GPIO 26/27/14  LED verde / amarelo / vermelho
 *   GPIO 25        buzzer
 *
 * Os indices usam a mesma escala dos sensores da base UCI Air Quality
 * (PT08.S2 e PT08.S1), entao o modelo da API le o mesmo numero que o ESP32 mede.
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define PIN_VOC      34
#define PIN_CO       35
#define PIN_DHT      15
#define PIN_VERDE    26
#define PIN_AMARELO  27
#define PIN_VERMELHO 14
#define PIN_BUZZER   25

// Limiares tirados da base real (mesmos da API e da Lambda)
const float VOC_ATENCAO = 830.0, VOC_CRITICO = 1140.0;   // fumaca e gases
const float CO_ATENCAO = 1010.0, CO_CRITICO = 1280.0;    // monoxido

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
// Troque pela Function URL da Lambda ou pelo endereco publico da API
const char* API_URL = "http://host.wokwi.internal:8000/ocorrencias";

const char* DISPOSITIVO_ID = "esp32-centro-01";
const float LATITUDE = -23.5505;
const float LONGITUDE = -46.6333;

DHT dht(PIN_DHT, DHT22);

float lerIndice(int pino, float minimo, float maximo) {
  return minimo + (analogRead(pino) / 4095.0) * (maximo - minimo);
}

// Classifica uma medida pelos seus dois limiares
String classificar(float valor, float atencao, float critico) {
  if (valor >= critico) return "critico";
  if (valor >= atencao) return "atencao";
  return "normal";
}

// Ar seco (abaixo de 30%) segura a fumaca perto do chao: so vira atencao, nunca critico
String classificarUmidade(float umid) {
  return umid < 30.0 ? "atencao" : "normal";
}

void alertar(const String& status) {
  digitalWrite(PIN_VERDE, status == "normal");
  digitalWrite(PIN_AMARELO, status == "atencao");
  digitalWrite(PIN_VERMELHO, status == "critico");
  if (status == "critico") tone(PIN_BUZZER, 1800, 600);
  else if (status == "atencao") tone(PIN_BUZZER, 950, 150);
  else noTone(PIN_BUZZER);
}

String montarJson(float gasVoc, float gasCo, float temp, float umid) {
  String j = "{";
  j += "\"dispositivo_id\":\"" + String(DISPOSITIVO_ID) + "\",";
  j += "\"tipo\":\"esp32\",";
  j += "\"latitude\":" + String(LATITUDE, 4) + ",";
  j += "\"longitude\":" + String(LONGITUDE, 4) + ",";
  j += "\"metrica\":\"gas_voc\",";
  j += "\"valor\":" + String(gasVoc, 1) + ",";
  j += "\"gas_co\":" + String(gasCo, 1) + ",";
  j += "\"temperatura_c\":" + String(temp, 1) + ",";
  j += "\"umidade_pct\":" + String(umid, 1);
  j += "}";
  return j;
}

void enviar(const String& json) {
  if (WiFi.status() != WL_CONNECTED) {
    // Sem rede a luz e o buzzer seguem funcionando; o ESP32 reconecta sozinho
    Serial.println("SEM REDE: alerta local ativo, leitura nao enviada");
    return;
  }
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(json);
  Serial.println("HTTP " + String(code));
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_VERDE, OUTPUT);
  pinMode(PIN_AMARELO, OUTPUT);
  pinMode(PIN_VERMELHO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  dht.begin();
  WiFi.begin(WIFI_SSID, WIFI_PASS);  // nao bloqueia: o alerta local funciona sem rede
}

void loop() {
  float gasVoc = lerIndice(PIN_VOC, 380.0, 2250.0);
  float gasCo = lerIndice(PIN_CO, 640.0, 2100.0);
  float temp = dht.readTemperature();
  float umid = dht.readHumidity();
  if (isnan(temp)) temp = 25.0;
  if (isnan(umid)) umid = 50.0;

  // A luz segue a medida de fumaca e gases (regra validada na base real: 84 de cada 100 horas).
  // As outras medidas tem status proprio no monitor serial e seguem para a central.
  String status = classificar(gasVoc, VOC_ATENCAO, VOC_CRITICO);
  String statusCo = classificar(gasCo, CO_ATENCAO, CO_CRITICO);
  String statusUmid = classificarUmidade(umid);
  alertar(status);

  String json = montarJson(gasVoc, gasCo, temp, umid);
  Serial.println("STATUS " + status);
  Serial.println("SENSORES gases=" + status + " monoxido=" + statusCo + " umidade=" + statusUmid +
                 " temperatura=" + String(temp, 1) + "C");
  Serial.println("JSON " + json);
  enviar(json);

  delay(3000);
}
