#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

WebServer server(80);

#define LED_PIN 2
#define MOTOR_PIN 18

void ledOn() {
  digitalWrite(LED_PIN, HIGH);
  server.send(200, "text/plain", "LED ON");
}

void ledOff() {
  digitalWrite(LED_PIN, LOW);
  server.send(200, "text/plain", "LED OFF");
}

void motorOn() {
  digitalWrite(MOTOR_PIN, HIGH);
  server.send(200, "text/plain", "MOTOR ON");
}

void motorOff() {
  digitalWrite(MOTOR_PIN, LOW);
  server.send(200, "text/plain", "MOTOR OFF");
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.println(WiFi.localIP());

  server.on("/led/on", ledOn);
  server.on("/led/off", ledOff);

  server.on("/motor/on", motorOn);
  server.on("/motor/off", motorOff);

  server.begin();
}

void loop() {
  server.handleClient();
}
