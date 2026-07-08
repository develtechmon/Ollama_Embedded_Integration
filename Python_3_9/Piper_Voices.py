import wave, io
import sounddevice as sd
import soundfile as sf
from piper import PiperVoice

voice = PiperVoice.load("en_US-lessac-medium.onnx")   # path to the file you just downloaded

# Piper writes into a WAV; we hand it an in-memory buffer instead of a disk file
buf = io.BytesIO()
with wave.open(buf, "wb") as wav_file:
    voice.synthesize_wav("Hello Lukas. If you can hear this, Piper works on three point nine.", wav_file)

buf.seek(0)
audio, sr = sf.read(buf)
sd.play(audio, sr)   # reusing the sounddevice you already proved with Whisper
sd.wait()