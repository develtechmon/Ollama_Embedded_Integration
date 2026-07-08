import sounddevice as sd
from faster_whisper import WhisperModel

# CPU + int8: fast enough for short commands, dodges the cuDNN DLL mess,
# and leaves your ~1.6 GB of free VRAM entirely to the LLM.
model = WhisperModel("base.en", device="cpu", compute_type="int8")

SECONDS, SR = 5, 16000
print("Speak now — recording 5 seconds...")
audio = sd.rec(int(SECONDS * SR), samplerate=SR, channels=1, dtype="float32")
sd.wait()
print("Transcribing...")

# segments is a GENERATOR — it doesn't transcribe until you iterate it,
# which is why we pull the text out in the join below.
segments, info = model.transcribe(audio.flatten(), language="en")
text = " ".join(s.text for s in segments).strip()
print("You said:", text)