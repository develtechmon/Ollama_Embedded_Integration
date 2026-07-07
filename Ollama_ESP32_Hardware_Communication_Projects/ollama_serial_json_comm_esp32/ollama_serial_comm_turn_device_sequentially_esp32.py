import ollama
import serial
import json

esp32 = serial.Serial(port='COM9', baudrate=115200, timeout=1)

MODEL = "qwen3.5:4b"

SYSTEM_PROMPT = """
You are a robot controller.

For every message, return ONE JSON object, one of two kinds:

Command (to control hardware) - include a short reply saying what you're doing:
{"type":"command","device":"led","action":"on","reply":"Okay, turning the LED on."}
{"type":"command","device":"motor","action":"off","reply":"Stopping the motor."}

Chat (anything that isn't a command - questions, greetings, small talk):
{"type":"chat","reply":"your short answer here"}

Devices: led, motor. Actions: on, off.
If it's not clearly a command, use chat.
Return only the JSON object, no code fences, no extra text.
"""

while True:
    user = input("Command: ")
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user}
        ],
        think=False,
        format="json"          # (1) rails: model must emit valid JSON, nothing else
    )

    reply = response['message']['content']
    try:
        cmd, _ = json.JSONDecoder().raw_decode(reply.strip())   # (2) eat first object, ignore trailing junk

        if cmd["type"] == "chat":
            print("Qwen:", cmd["reply"])

        elif cmd["type"] == "command":
            sent = False
            if cmd["device"] == "led":
                if cmd["action"] == "on":
                    esp32.write(b"LED_ON\n"); sent = True
                    print("LED ON command sent to ESP32")
                elif cmd["action"] == "off":
                    esp32.write(b"LED_OFF\n"); sent = True
                    print("LED OFF command sent to ESP32")

            elif cmd["device"] == "motor":
                if cmd["action"] == "on":
                    esp32.write(b"MOTOR_ON\n"); sent = True
                    print("MOTOR ON command sent to ESP32")
                elif cmd["action"] == "off":
                    esp32.write(b"MOTOR_OFF\n"); sent = True
                    print("MOTOR OFF command sent to ESP32")

            if sent:
                print("Qwen:", cmd.get("reply", "Done."))

    except Exception as e:
        print("Invalid response:", e)