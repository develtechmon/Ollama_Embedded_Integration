import io, wave
import sounddevice as sd, soundfile as sf, ollama
from faster_whisper import WhisperModel
from piper import PiperVoice

MODEL, SR = "qwen3.5:4b", 16000
whisper = WhisperModel("base.en", device="cpu", compute_type="int8")
voice = PiperVoice.load("en_US-lessac-medium.onnx")

client = ollama.Client(host="http://127.0.0.1:11434")

def set_led(state: bool) -> str:            # fake now; swap for real ESP32 serial later
    print(f"   >>> [hardware] set_led({state})"); return "on" if state else "off"

TOOLS = [{"type":"function","function":{"name":"set_led",
    "description":"Turn the LED on or off.",
    "parameters":{"type":"object",
        "properties":{"state":{"type":"boolean","description":"True=on, False=off"}},
        "required":["state"]}}}]
DISPATCH = {"set_led": set_led}

def listen(sec=5):
    input("\n[Enter, then speak a command...] ")
    a = sd.rec(int(sec*SR), samplerate=SR, channels=1, dtype="float32"); sd.wait()
    segs, _ = whisper.transcribe(a.flatten(), language="en", vad_filter=True)
    return " ".join(s.text for s in segs).strip()

def say(text):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w: voice.synthesize_wav(text, w)
    buf.seek(0); data, sr = sf.read(buf); sd.play(data, sr); sd.wait()

print("LED voice control ready. Say 'quit' to exit.")
while True:
    cmd = listen()
    if not cmd: print("(nothing heard)"); continue
    print("You:", cmd)
    if "quit" in cmd.lower(): break
    msgs = [{"role":"user","content":cmd}]
    r = client.chat(model=MODEL, messages=msgs, tools=TOOLS, think=False)
    if r.message.tool_calls:
        msgs.append(r.message)
        for c in r.message.tool_calls:
            fn = DISPATCH.get(c.function.name)
            res = fn(**c.function.arguments) if fn else "unknown"
            msgs.append({"role":"tool","tool_name":c.function.name,"content":str(res)})
        final = client.chat(model=MODEL, messages=msgs, tools=TOOLS, think=False)
        say(final.message.content or "Done.")
    else:
        say(r.message.content or "I didn't catch a command.")   # abstains — no LED fire