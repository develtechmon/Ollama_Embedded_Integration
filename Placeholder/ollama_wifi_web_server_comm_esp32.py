import ollama
import requests

ESP32_IP = "192.168.1.88"

# -------------------
# Hardware Functions
# -------------------

def turn_on_led():
    requests.get(f"http://{ESP32_IP}/led/on")
    return "LED turned ON"


def turn_off_led():
    requests.get(f"http://{ESP32_IP}/led/off")
    return "LED turned OFF"


def start_motor():
    requests.get(f"http://{ESP32_IP}/motor/on")
    return "Motor started"


def stop_motor():
    requests.get(f"http://{ESP32_IP}/motor/off")
    return "Motor stopped"

# -------------------
# Tool Registry
# -------------------

FUNCTION_MAP = {
    "turn_on_led": turn_on_led,
    "turn_off_led": turn_off_led,
    "start_motor": start_motor,
    "stop_motor": stop_motor
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "turn_on_led",
            "description": "Turn ON LED"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "turn_off_led",
            "description": "Turn OFF LED"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_motor",
            "description": "Start motor"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_motor",
            "description": "Stop motor"
        }
    }
]

MODEL = "qwen3:8b"

while True:

    user_input = input("You: ")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ],
        tools=TOOLS
    )

    message = response["message"]

    if message.get("tool_calls"):

        for tool in message["tool_calls"]:

            fn_name = tool["function"]["name"]

            result = FUNCTION_MAP

            print("EXECUTED:", result)

    else:
        print(message["content"])
