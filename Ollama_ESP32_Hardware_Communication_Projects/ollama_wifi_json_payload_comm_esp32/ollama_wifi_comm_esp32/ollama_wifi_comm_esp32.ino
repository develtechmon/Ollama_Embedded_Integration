#include <WiFi.h>

#define LED_PIN 5
#define MOTOR_PIN 4

const char* ssid = "Galaxy S24 Ultra 0997";
const char* password = "Lukas@92";

WiFiServer server(8080);   // listen on port 8080
String command = "";

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }

  Serial.println("\nConnected. ESP32 IP:");
  Serial.println(WiFi.localIP());   // <-- put THIS number into your Python
  server.begin();
}

void loop() {
  WiFiClient client = server.available();   // someone dialed in?
  if (client) {
    client.setNoDelay(true);                // don't buffer tiny commands, send now
    while (client.connected()) {
      if (client.available()) {
        command = client.readStringUntil('\n');
        command.trim();

        if (command == "LED_ON")        { digitalWrite(LED_PIN, HIGH); client.println("OK LED_ON"); }
        else if (command == "LED_OFF")  { digitalWrite(LED_PIN, LOW);  client.println("OK LED_OFF"); }
        else if (command == "MOTOR_ON") { digitalWrite(MOTOR_PIN, HIGH); client.println("OK MOTOR_ON"); }
        else if (command == "MOTOR_OFF"){ digitalWrite(MOTOR_PIN, LOW);  client.println("OK MOTOR_OFF"); }
        else if (command.length() > 0)  { client.println("UNKNOWN " + command); }
      }
    }
    client.stop();   // caller hung up
  }
}