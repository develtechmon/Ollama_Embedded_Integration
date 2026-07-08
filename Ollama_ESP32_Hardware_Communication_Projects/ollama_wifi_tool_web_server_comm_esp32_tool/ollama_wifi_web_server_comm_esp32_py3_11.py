import ollama
import requests

ESP32_IP = "10.46.237.153"
MODEL = "qwen3.5:4b"
client = ollama.Client(host="http://127.0.0.1:11434")

# --- Hardware functions: docstring + type hint ARE the tool schema now ---
def _send(path):
    try:
        r = requests.get(f"http://{ESP32_IP}{path}", timeout=3)
        return r.text
    except requests.exceptions.RequestException as e:
        return f"FAILED ({e})"

def turn_on_led() -> str:
    """Turn the LED light ON. Use when the user wants light, to switch on the led, illuminate, or brighten."""
    return _send("/led/on")

def turn_off_led() -> str:
    """Turn the LED light OFF. Use when the user wants the led off, darkness, or to kill the light."""
    return _send("/led/off")

def start_motor() -> str:
    """Start / turn the motor ON. Use when the user wants the motor running, spinning, or to start moving."""
    return _send("/motor/on")

def stop_motor() -> str:
    """Stop / turn the motor OFF. Use when the user wants the motor stopped, halted, or to stop moving."""
    return _send("/motor/off")

FUNCTION_MAP = {
    "turn_on_led": turn_on_led,
    "turn_off_led": turn_off_led,
    "start_motor": start_motor,
    "stop_motor": stop_motor,
}
TOOLS = [turn_on_led, turn_off_led, start_motor, stop_motor]   # pass functions directly

while True:
    user_input = input("You: ")
    response = client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
        tools=TOOLS,
        think=False,
    )
    message = response["message"]
    tool_calls = message.get("tool_calls")
    if tool_calls:
        for tool in tool_calls:
            fn_name = tool["function"]["name"]
            if fn_name in FUNCTION_MAP:
                result = FUNCTION_MAP[fn_name]()
                print("EXECUTED:", fn_name, "->", result)
            else:
                print("Unknown tool:", fn_name)
    else:
        print("Qwen:", message.get("content", ""))