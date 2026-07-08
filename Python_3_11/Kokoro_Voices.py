import sounddevice as sd
from kokoro_onnx import Kokoro

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

samples, sample_rate = kokoro.create(
    "Hello Lukas. If you can hear this, Kokoro finally works, thanks to Python three eleven.",
    voice="af_heart",
    speed=1.0,
    lang="en-us",
)
sd.play(samples, sample_rate)
sd.wait()