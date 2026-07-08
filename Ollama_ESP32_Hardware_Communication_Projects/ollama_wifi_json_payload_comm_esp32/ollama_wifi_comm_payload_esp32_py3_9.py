import ollama
import socket
import json

ESP32_IP = "10.46.237.153"   # <-- the IP the ESP32 printed on boot
ESP32_PORT = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)                     # don't hang forever waiting for an ack
sock.connect((ESP32_IP, ESP32_PORT))   # "dial" the ESP32
netf = sock.makefile("r")              # gives us .readline(), just like serial

MODEL = "qwen3.5:4b"

client = ollama.Client(host="http://127.0.0.1:11434")

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
            for a in cmd.get("actions", []):
                payload = CMD.get((a["device"], a["action"]))
                if payload:
                    sock.sendall(payload)              # was esp32.write()
                    sent = True
                    try:
                        ack = netf.readline().strip()  # was esp32.readline()
                        print("ESP32:", ack if ack else "(no reply)")
                    except socket.timeout:
                        print("ESP32: (timeout - no ack)")

            if sent:
                print("Qwen:", cmd.get("reply", "Done."))

    except Exception as e:
        print("Invalid response:", e)