import requests
import ollama
import json

ESP32_IP = "192.168.1.50"

MODEL = "qwen3:8b"

prompt = """
Convert commands into JSON.

Turn on LED
{"command":"LED_ON"}

Turn off LED
{"command":"LED_OFF"}

Start motor
{"command":"MOTOR_ON"}

Stop motor
{"command":"MOTOR_OFF"}

JSON only.
"""

while True:

    user = input("Command:")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role":"system","content":prompt},
            {"role":"user","content":user}
        ]
    )

    reply = response["message"]["content"]

    print(reply)

    data = json.loads(reply)

    requests.get(
        f"http://{ESP32_IP}/command",
        params={"cmd": data["command"]}
    )
