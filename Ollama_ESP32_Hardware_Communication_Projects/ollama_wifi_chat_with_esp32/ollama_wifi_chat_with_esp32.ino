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
  HTTPClient http;
  http.begin(OLLAMA_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(60000);   // model can take a while on first token — 60s is safe

  // Build the request body. stream:false = one lump reply (easier).
  // Escape quotes and newlines in the prompt so we don't break the JSON.
  String safe = prompt;
  safe.replace("\\", "\\\\");
  safe.replace("\"", "\\\"");
  safe.replace("\n", "\\n");

  String body = String("{\"model\":\"") + MODEL +
                "\",\"prompt\":\"" + safe +
                "\",\"stream\":false,\"think\":false}";

  int code = http.POST(body);
  if (code == 200) {
    String reply = http.getString();
    // Ollama returns JSON like {"response":"...","done":true,...}
    // Cheap extract without a JSON lib — find "response":"..." field.
    int keyPos = reply.indexOf("\"response\":\"");
    if (keyPos >= 0) {
      int start = keyPos + 12;                       // past `"response":"`
      int end = reply.indexOf("\",\"done\"", start); // Ollama always follows response with ,"done"
      if (end > start) {
        String answer = reply.substring(start, end);
        answer.replace("\\n", "\n");
        answer.replace("\\\"", "\"");
        Serial.println("\nQwen: " + answer + "\n");
      } else {
        Serial.println("Parse fail. Raw: " + reply);
      }
    } else {
      Serial.println("No response field. Raw: " + reply);
    }
  } else {
    Serial.printf("HTTP %d — %s\n", code, http.errorToString(code).c_str());
  }
  http.end();
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
