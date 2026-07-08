#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Galaxy S24 Ultra 0997";
const char* password = "Lukas@92";        // change the exposed one

// Your G14's IP on the same WiFi/hotspot (from ipconfig)
const char* OLLAMA_URL = "http://10.68.173.137:11434/api/generate";
const char* MODEL      = "qwen3.5:4b";

String userMessage = "";

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.print(" OK, IP: "); Serial.println(WiFi.localIP());
}

void askOllama(const String& prompt) {
  String safe = prompt;
  safe.replace("\\", "\\\\");
  safe.replace("\"", "\\\"");
  safe.replace("\n", "\\n");

  String body = String("{\"model\":\"") + MODEL +
                "\",\"prompt\":\"" + safe +
                "\",\"stream\":false,\"think\":false,\"keep_alive\":-1}";

  for (int attempt = 1; attempt <= 3; attempt++) {
    WiFiClient client;             // fresh socket every attempt — key
    HTTPClient http;
    http.begin(client, OLLAMA_URL);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(60000);
    http.setReuse(false);          // don't reuse keep-alive connection

    int code = http.POST(body);

    if (code == 200) {
      String reply = http.getString();
      int keyPos = reply.indexOf("\"response\":\"");
      if (keyPos >= 0) {
        int start = keyPos + 12;
        int end = reply.indexOf("\",\"done\"", start);
        if (end > start) {
          String answer = reply.substring(start, end);
          answer.replace("\\n", "\n");
          answer.replace("\\\"", "\"");
          Serial.println("\nQwen: " + answer + "\n");
        }
      }
      http.end();
      return;                      // success — bail out
    }

    Serial.printf("Attempt %d: HTTP %d, retrying...\n", attempt, code);
    http.end();
    delay(1500);                   // give hotspot / stack a beat
  }

  Serial.println("Gave up after 3 attempts.");
}

void setup() {
  Serial.begin(115200);
  delay(500);
  connectWiFi();
  Serial.println("Type a message and press Enter:");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      userMessage.trim();
      if (userMessage.length() > 0) {
        Serial.println("You: " + userMessage);
        Serial.println("(thinking...)");
        askOllama(userMessage);
        userMessage = "";
        Serial.println("Type a message:");
      }
    } else {
      userMessage += c;
    }
  }
}
