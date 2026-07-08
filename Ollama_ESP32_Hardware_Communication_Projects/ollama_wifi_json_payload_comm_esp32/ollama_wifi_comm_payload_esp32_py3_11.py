import ollama
import socket

ESP32_IP = "10.46.237.153"
ESP32_PORT = 8080
MODEL = "qwen3.5:4b"
client = ollama.Client(host="http://127.0.0.1:11434")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
sock.connect((ESP32_IP, ESP32_PORT))
netf = sock.makefile("r")

def _send(payload: bytes) -> str:
    sock.sendall(payload)
    try:
        ack = netf.readline().strip()
        return ack if ack else "(no reply)"
    except socket.timeout:
        return "(timeout - no ack)"

def turn_on_led() -> str:
    """Turn the LED light ON. Use when the user wants light, to switch on the led, illuminate, or brighten."""
    return _send(b"LED_ON\n")

def turn_off_led() -> str:
    """Turn the LED light OFF. Use when the user wants the led off, darkness, or to kill the light."""
    return _send(b"LED_OFF\n")

def start_motor() -> str:
    """Start / turn the motor ON. Use when the user wants the motor running, spinning, or to start moving."""
    return _send(b"MOTOR_ON\n")

def stop_motor() -> str:
    """Stop / turn the motor OFF. Use when the user wants the motor stopped, halted, or to stop moving."""
    return _send(b"MOTOR_OFF\n")

FUNCTION_MAP = {"turn_on_led": turn_on_led, "turn_off_led": turn_off_led,
                "start_motor": start_motor, "stop_motor": stop_motor}
TOOLS = [turn_on_led, turn_off_led, start_motor, stop_motor]

while True:
    user_input = input("You: ")
    response = client.chat(model=MODEL, messages=[{"role": "user", "content": user_input}],
                           tools=TOOLS, think=False)
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