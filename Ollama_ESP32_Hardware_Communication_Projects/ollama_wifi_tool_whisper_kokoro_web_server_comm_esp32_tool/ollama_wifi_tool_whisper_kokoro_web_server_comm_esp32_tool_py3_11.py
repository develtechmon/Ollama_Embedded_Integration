import ollama
import requests
import sounddevice as sd
from faster_whisper import WhisperModel
from kokoro_onnx import Kokoro

ESP32_IP = "10.46.237.153"
MODEL, SR = "qwen3.5:4b", 16000
client = ollama.Client(host="http://127.0.0.1:11434")

whisper = WhisperModel("base.en", device="cpu", compute_type="int8")
kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

def listen(sec=5):
    input("\n[Enter, then speak a command...] ")
    a = sd.rec(int(sec*SR), samplerate=SR, channels=1, dtype="float32"); sd.wait()
    segs, _ = whisper.transcribe(a.flatten(), language="en", vad_filter=True)
    return " ".join(s.text for s in segs).strip()

def say(text):
    samples, sr = kokoro.create(text, voice="af_heart", speed=1.0, lang="en-us")
    sd.play(samples, sr); sd.wait()

# --- Hardware functions: doubling as tool schemas via docstring + type hints ---
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

FUNCTION_MAP = {"turn_on_led": turn_on_led, "turn_off_led": turn_off_led,
                "start_motor": start_motor, "stop_motor": stop_motor}
TOOLS = [turn_on_led, turn_off_led, start_motor, stop_motor]

print("Voice-controlled ESP32 ready. Say 'quit' to exit.")
while True:
    user_input = listen()
    if not user_input:
        print("(nothing heard)")
        continue
    print("You:", user_input)
    if "quit" in user_input.lower():
        break

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
                say(f"Done, {fn_name.replace('_', ' ')}.")
            else:
                print("Unknown tool:", fn_name)
                say("I don't know how to do that.")
    else:
        reply = message.get("content", "")
        print("Qwen:", reply)
        say(reply if reply else "I didn't catch a command.")