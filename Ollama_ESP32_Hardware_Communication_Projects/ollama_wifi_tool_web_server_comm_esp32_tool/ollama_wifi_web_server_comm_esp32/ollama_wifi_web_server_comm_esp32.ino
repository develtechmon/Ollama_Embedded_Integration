#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Galaxy S24 Ultra 0997";
const char* password = "Lukas@92";   // change it — the old one is public now

WebServer server(80);

#define LED_PIN 5
#define MOTOR_PIN 4

void ledOn()    { digitalWrite(LED_PIN, HIGH);   server.send(200, "text/plain", "LED ON"); }
void ledOff()   { digitalWrite(LED_PIN, LOW);    server.send(200, "text/plain", "LED OFF"); }
void motorOn()  { digitalWrite(MOTOR_PIN, HIGH); server.send(200, "text/plain", "MOTOR ON"); }
void motorOff() { digitalWrite(MOTOR_PIN, LOW);  server.send(200, "text/plain", "MOTOR OFF"); }
void notFound() { server.send(404, "text/plain", "Unknown route"); }

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.print("\nIP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);

  connectWiFi();

  server.on("/led/on", ledOn);
  server.on("/led/off", ledOff);
  server.on("/motor/on", motorOn);
  server.on("/motor/off", motorOff);
  server.onNotFound(notFound);
  server.begin();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();   // hotspot dropped -> rejoin, don't die
  server.handleClient();
}