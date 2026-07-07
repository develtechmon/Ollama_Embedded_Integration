// =====================================================
// ESP32-S3 Super Mini
// Cytron Maker Drive + Encoder + LED + LLM Control
// Compatible with your Python Voice_LLM script
// =====================================================


// ============================
// LED
// ============================
const int LED_PIN = 5;


// ============================
// Encoder Pins
// ============================
const int encoderA = 8;
const int encoderB = 9;


// ============================
// Motor Driver Pins
// ============================
const int motorM2A = 7;
const int motorM2B = 6;


// ============================
// Encoder Variables
// ============================
volatile long pulseCount = 0;


// ============================
// Motion Variables
// ============================
long targetPulse = 0;

bool motorEnabled = false;
bool targetReached = false;


// ============================
// PID Parameters
// ============================
float Kp = 1.2;
float Ki = 0.0;
float Kd = 0.08;


// ============================
// PID Variables
// ============================
float error = 0;
float previousError = 0;
float integral = 0;
float derivative = 0;

int motorPWM = 0;


// ============================
// Motor Settings
// ============================
const int maxPWM = 130;
const int minPWM = 45;

const int stopRange = 2;


// ============================
// Timing
// ============================
unsigned long lastPIDTime = 0;
const unsigned long pidInterval = 20;


// =====================================================
// Encoder ISR
// =====================================================
void IRAM_ATTR readEncoder()
{
  int B = digitalRead(encoderB);

  if (B == HIGH)
  {
    pulseCount++;
  }
  else
  {
    pulseCount--;
  }
}


// =====================================================
// Motor Functions
// =====================================================
void motorForward(int speedValue)
{
  analogWrite(motorM2A, speedValue);
  analogWrite(motorM2B, 0);
}

void motorReverse(int speedValue)
{
  analogWrite(motorM2A, 0);
  analogWrite(motorM2B, speedValue);
}

void stopMotor()
{
  analogWrite(motorM2A, 0);
  analogWrite(motorM2B, 0);
}


// =====================================================
// Start Motion
// =====================================================
void startMove(long pulses)
{
  noInterrupts();
  pulseCount = 0;
  interrupts();

  integral = 0;
  previousError = 0;
  derivative = 0;

  targetPulse = pulses;

  targetReached = false;
  motorEnabled = true;
}


// =====================================================
// PID Control
// =====================================================
void runPID()
{
  if (!motorEnabled)
  {
    stopMotor();
    return;
  }

  long currentPulse;

  noInterrupts();
  currentPulse = pulseCount;
  interrupts();

  error = targetPulse - currentPulse;

  if (abs(error) <= stopRange)
  {
    stopMotor();

    motorEnabled = false;
    targetReached = true;

    integral = 0;
    previousError = error;

    Serial.println("TARGET_REACHED");

    return;
  }

  integral += error;

  integral = constrain(
    integral,
    -300,
    300
  );

  derivative = error - previousError;

  float output =
      (Kp * error) +
      (Ki * integral) +
      (Kd * derivative);

  previousError = error;

  output = constrain(
      output,
      -maxPWM,
      maxPWM);

  motorPWM = abs(output);

  if (motorPWM > 0 && motorPWM < minPWM)
  {
    motorPWM = minPWM;
  }

  // Soft slowdown near target
  if (abs(error) < 50)
  {
    motorPWM = min(motorPWM, 80);
  }

  if (abs(error) < 20)
  {
    motorPWM = min(motorPWM, 60);
  }

  if (output > 0)
  {
    motorForward(motorPWM);
  }
  else
  {
    motorReverse(motorPWM);
  }
}


// =====================================================
// STATUS Command
// =====================================================
void sendStatus()
{
  long currentPulse;

  noInterrupts();
  currentPulse = pulseCount;
  interrupts();

  Serial.print("Pulse=");
  Serial.print(currentPulse);

  Serial.print(",Target=");
  Serial.print(targetPulse);

  Serial.print(",Error=");
  Serial.print(error);

  Serial.print(",PWM=");
  Serial.print(motorPWM);

  Serial.print(",State=");

  if (motorEnabled)
  {
    Serial.println("MOVING");
  }
  else if (targetReached)
  {
    Serial.println("REACHED");
  }
  else
  {
    Serial.println("IDLE");
  }
}


// =====================================================
// Command Processing
// =====================================================
void processCommand(String cmd)
{
  cmd.trim();

  // -------------------------
  // PING
  // -------------------------
  if (cmd == "PING")
  {
    Serial.println("PONG");
    return;
  }

  // -------------------------
  // LED ON
  // -------------------------
  if (cmd == "LED:1")
  {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("OK:LED_ON");
    return;
  }

  // -------------------------
  // LED OFF
  // -------------------------
  if (cmd == "LED:0")
  {
    digitalWrite(LED_PIN, LOW);
    Serial.println("OK:LED_OFF");
    return;
  }

  // -------------------------
  // MOTOR STOP
  // -------------------------
  if (cmd == "MOTOR:STOP")
  {
    motorEnabled = false;
    stopMotor();

    Serial.println("OK:MOTOR_STOPPED");
    return;
  }

  // -------------------------
  // STATUS
  // -------------------------
  if (cmd == "STATUS")
  {
    sendStatus();
    return;
  }

  // -------------------------
  // MOTOR:FWD:330
  // -------------------------
  if (cmd.startsWith("MOTOR:FWD:"))
  {
    String pulseText = cmd.substring(10);

    long pulses = pulseText.toInt();

    if (pulses <= 0)
    {
      pulses = 330;
    }

    startMove(pulses);

    Serial.println("OK:MOTOR_FORWARD");
    return;
  }

  // -------------------------
  // MOTOR:REV:330
  // -------------------------
  if (cmd.startsWith("MOTOR:REV:"))
  {
    String pulseText = cmd.substring(10);

    long pulses = pulseText.toInt();

    if (pulses <= 0)
    {
      pulses = 330;
    }

    startMove(-pulses);

    Serial.println("OK:MOTOR_REVERSE");
    return;
  }

  Serial.println("ERR");
}


// =====================================================
// Serial Processing
// =====================================================
void checkSerial()
{
  if (!Serial.available())
  {
    return;
  }

  String cmd = Serial.readStringUntil('\n');

  processCommand(cmd);
}


// =====================================================
// Setup
// =====================================================
void setup()
{
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);

  pinMode(encoderA, INPUT_PULLUP);
  pinMode(encoderB, INPUT_PULLUP);

  pinMode(motorM2A, OUTPUT);
  pinMode(motorM2B, OUTPUT);

  digitalWrite(LED_PIN, LOW);

  stopMotor();

  attachInterrupt(
      digitalPinToInterrupt(encoderA),
      readEncoder,
      RISING);

  delay(1000);

  Serial.println("ESP32 LLM Controller Ready");

  noInterrupts();
  pulseCount = 0;
  interrupts();

  lastPIDTime = millis();
}


// =====================================================
// Main Loop
// =====================================================
void loop()
{
  checkSerial();

  unsigned long now = millis();

  if (now - lastPIDTime >= pidInterval)
  {
    runPID();
    lastPIDTime = now;
  }
}