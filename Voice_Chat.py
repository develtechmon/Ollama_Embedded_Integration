import io, wave
import sounddevice as sd, soundfile as sf, ollama
from faster_whisper import WhisperModel
from piper import PiperVoice

MODEL, SR = "qwen3.5:4b", 16000
whisper = WhisperModel("base.en", device="cpu", compute_type="int8")
voice = PiperVoice.load("en_US-lessac-high.onnx")

def listen(sec=5):
    input("\n[Enter, then speak...] ")
    a = sd.rec(int(sec*SR), samplerate=SR, channels=1, dtype="float32"); sd.wait()
    segs, _ = whisper.transcribe(a.flatten(), language="en", vad_filter=True)
    return " ".join(s.text for s in segs).strip()

def say(text):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w: voice.synthesize_wav(text, w)
    buf.seek(0); data, sr = sf.read(buf); sd.play(data, sr); sd.wait()

msgs = [{"role":"system","content":"You are a friendly robot voice assistant. Reply naturally in one short sentence. Use simple words and natural punctuation for speech."}]
print("Voice chat ready. Say 'quit' to exit.")
while True:
    u = listen()
    if not u: print("(nothing heard)"); continue
    print("You:", u)
    if "quit" in u.lower(): break
    msgs.append({"role":"user","content":u})
    reply = ollama.chat(model=MODEL, messages=msgs, think=False).message.content
    msgs.append({"role":"assistant","content":reply})
    print("AI:", reply); say(reply)