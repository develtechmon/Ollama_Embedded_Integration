import ollama
import serial
import json

# ESP32 Serial Port
esp32 = serial.Serial(
    port='COM5',   # Windows
    baudrate=115200,
    timeout=1
)

MODEL = "qwen3:8b"

SYSTEM_PROMPT = """
You are a robot controller.

Convert user commands into JSON only.

Examples:

Turn on the led
{"device":"led","action":"on"}

Turn off led
{"device":"led","action":"off"}

Start motor
{"device":"motor","action":"on"}

Stop motor
{"device":"motor","action":"off"}

Only return JSON.
"""


while True:
    user = input("Command: ")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user
            }
        ]
    )

    reply = response['message']['content']

    print("Qwen:", reply)

    try:
        cmd = json.loads(reply)

        if cmd["device"] == "led":

            if cmd["action"] == "on":
                esp32.write(b"LED_ON\n")

            elif cmd["action"] == "off":
                esp32.write(b"LED_OFF\n")

        elif cmd["device"] == "motor":

            if cmd["action"] == "on":
                esp32.write(b"MOTOR_ON\n")

            elif cmd["action"] == "off":
                esp32.write(b"MOTOR_OFF\n")

    except Exception as e:
        print("Invalid response:", e)
