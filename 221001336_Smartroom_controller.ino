#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "Galaxy A11";
const char* password = "Chidu@2022";
const char* server_ip = "http://192.168.151.96:5000";

const int LED_PIN = 2;
const int FAN_PIN = 4;
const int LDR_PIN = 34;
const int POT_PIN = 35;
const int BUTTON_PIN = 12;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(1000);
  Serial.println("Connected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Read sensors
    int brightness = analogRead(LDR_PIN);
    int fanPot = analogRead(POT_PIN);
    bool motion = digitalRead(BUTTON_PIN) == LOW;

    // Send sensor data
    DynamicJsonDocument sensorDoc(128);
    sensorDoc["analog_input"] = brightness;
    sensorDoc["button"] = motion;
    sensorDoc["fan_pot"] = fanPot;

    String payload;
    serializeJson(sensorDoc, payload);
    
    http.begin(String(server_ip) + "/esp/update");
    http.addHeader("Content-Type", "application/json");
    http.POST(payload);
    http.end();

    // Get controls
    http.begin(String(server_ip) + "/esp/control");
    if (http.GET() == HTTP_CODE_OK) {
      String response = http.getString();
      DynamicJsonDocument controlDoc(128);
      deserializeJson(controlDoc, response);

      bool ledOn = controlDoc["led_enabled"];
      int ledBrightness = controlDoc["brightness"];
      bool fanOn = controlDoc["fan_enabled"];
      int fanSpeed = controlDoc["fan_speed"];

      analogWrite(LED_PIN, ledOn ? ledBrightness : 0);
      analogWrite(FAN_PIN, fanOn ? fanSpeed : 0);
    }
    http.end();
  }
  delay(500);
}