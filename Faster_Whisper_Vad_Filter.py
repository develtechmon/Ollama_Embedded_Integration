import sounddevice as sd
from faster_whisper import WhisperModel

model = WhisperModel("base.en", device="cpu", compute_type="int8")

SECONDS, SR = 5, 16000
print("Speak now — recording 5 seconds...")
audio = sd.rec(int(SECONDS * SR), samplerate=SR, channels=1, dtype="float32")
sd.wait()
print("Transcribing...")

# vad_filter=True: strip silence/non-speech BEFORE transcribing, so dead air
# at the start doesn't get hallucinated into a fake word like "Martichot".
segments, info = model.transcribe(audio.flatten(), language="en", vad_filter=True)
text = " ".join(s.text for s in segments).strip()
print("You said:", text if text else "(nothing heard)")