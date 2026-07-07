const int LED_PIN = 5;   // external LED + 220Ω on a free GPIO.
                         // S3 onboard-LED pin varies by board; external is foolproof.
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}
void loop() {
  if (!Serial.available()) return;
  String c = Serial.readStringUntil('\n'); c.trim();
  if      (c == "LED:1") { digitalWrite(LED_PIN, HIGH); Serial.println("OK:ON"); }
  else if (c == "LED:0") { digitalWrite(LED_PIN, LOW);  Serial.println("OK:OFF"); }
  else if (c == "PING")  { Serial.println("PONG"); }
  else                     Serial.println("ERR");
}