#define LED_PIN 5
#define MOTOR_PIN 4

String command = "";

void setup()
{
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);
}

void loop()
{
  if (Serial.available())
  {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "LED_ON")
    {
      digitalWrite(LED_PIN, HIGH);
    }

    else if (command == "LED_OFF")
    {
      digitalWrite(LED_PIN, LOW);
    }

    else if (command == "MOTOR_ON")
    {
      digitalWrite(MOTOR_PIN, HIGH);
    }

    else if (command == "MOTOR_OFF")
    {
      digitalWrite(MOTOR_PIN, LOW);
    }
  }
}
