import ollama
import serial
import json
import time

esp32 = serial.Serial(port='COM9', baudrate=115200, timeout=1)
time.sleep(2)                 # let ESP32 finish booting
esp32.reset_input_buffer()    # throw away boot text before we start

client = ollama.Client(host="http://127.0.0.1:11434")

MODEL = "qwen3.5:4b"

SYSTEM_PROMPT = """
You are a robot controller.

For every message, return ONE JSON object, one of two kinds:

Command (control hardware) - "actions" is a LIST, one entry per device to change:
{"type":"command","actions":[{"device":"led","action":"on"}],"reply":"Turning the LED on."}
{"type":"command","actions":[{"device":"led","action":"off"},{"device":"motor","action":"off"}],"reply":"Turning both off."}

Chat (anything that isn't a command):
{"type":"chat","reply":"your short answer here"}

Devices: led, motor. Actions: on, off.
Put as many entries in "actions" as the user asks for.
Return only the JSON object, no code fences, no extra text.
"""

CMD = {
    ("led", "on"):    b"LED_ON\n",
    ("led", "off"):   b"LED_OFF\n",
    ("motor", "on"):  b"MOTOR_ON\n",
    ("motor", "off"): b"MOTOR_OFF\n",
}

while True:
    user = input("Command: ")
    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user}
        ],
        think=False,
        format="json"
    )

    reply = response['message']['content']
    try:
        cmd, _ = json.JSONDecoder().raw_decode(reply.strip())

        if cmd["type"] == "chat":
            print("Qwen:", cmd["reply"])

        elif cmd["type"] == "command":
            sent = False
            for a in cmd.get("actions", []):          # .get: no crash if key missing
                payload = CMD.get((a["device"], a["action"]))
                if payload:
                    esp32.write(payload); sent = True
                    ack = esp32.readline().decode(errors="ignore").strip()
                    print("ESP32:", ack if ack else "(no reply)")

            if sent:
                print("Qwen:", cmd.get("reply", "Done."))

    except Exception as e:
        print("Invalid response:", e)