import io
import wave
import time
import cv2
import ollama
import sounddevice as sd
import soundfile as sf

from faster_whisper import WhisperModel
from piper import PiperVoice

# ============================================================
# SETTINGS
# ============================================================

MODEL = "qwen3.5:4b"
SR = 16000

CAMERA_INDEX = 0
IMAGE_FILE = "camera_frame.jpg"

WHISPER_MODEL = "base.en"
PIPER_VOICE_FILE = "en_US-lessac-medium.onnx"


# ============================================================
# LOAD AI MODELS
# ============================================================

print("Loading Whisper...")
whisper = WhisperModel(
    WHISPER_MODEL,
    device="cpu",
    compute_type="int8"
)
print("Whisper loaded.")

print("Loading Piper voice...")
voice = PiperVoice.load(PIPER_VOICE_FILE)
print("Piper loaded.")


# ============================================================
# LISTEN FUNCTION
# ============================================================

def listen(sec=5):
    input("\n[Press ENTER, then speak...] ")
    audio = sd.rec(
        int(sec * SR),
        samplerate=SR,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    segments, _ = whisper.transcribe(
        audio.flatten(),
        language="en",
        vad_filter=True
    )

    text = " ".join(
        segment.text for segment in segments
    ).strip()
    return text

# ============================================================
# TEXT TO SPEECH FUNCTION
# ============================================================

def say(text):
    if not text:
        text = "I have nothing to say."
    print("AI:", text)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    buf.seek(0)
    data, sr = sf.read(buf)
    sd.play(data, sr)
    sd.wait()

# ============================================================
# CAMERA FUNCTION
# ============================================================

def capture_image():
    print("Opening camera...")
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        return None, "Camera not found. Please check the camera index."
    time.sleep(1)
    ret, frame = camera.read()
    camera.release()
    if not ret:
        return None, "Failed to capture image from camera."
    cv2.imwrite(IMAGE_FILE, frame)
    print("Image captured:", IMAGE_FILE)
    return IMAGE_FILE, None

# ============================================================
# ASK QWEN ABOUT CAMERA IMAGE
# ============================================================

def ask_qwen_vision(image_path, user_question):
    vision_prompt = f"""
                    You are a helpful robot vision assistant.
                    Look carefully at the image and answer the user's question.
                    User question:
                    {user_question}

                    Reply in one or two short sentences because your response will be spoken aloud.
                    """

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": vision_prompt,
                "images": [image_path]
            }
        ],
        think=False
    )
    return response.message.content

# ============================================================
# NORMAL QWEN CHAT
# ============================================================
messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly voice assistant. "
            "Reply in one or two short sentences because your response will be spoken aloud."
        )
    }
]

def ask_qwen_text(user_text):
    messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        think=False
    )

    reply = response.message.content
    messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )
    return reply

# ============================================================
# CAMERA INTENT DETECTION
# ============================================================
def is_camera_question(text):
    text = text.lower()
    camera_keywords = [
        "camera",
        "look",
        "see",
        "what do you see",
        "describe",
        "image",
        "picture",
        "photo",
        "obstacle",
        "object",
        "in front",
        "ahead",
        "detect"
    ]

    for keyword in camera_keywords:
        if keyword in text:
            return True
    return False

# ============================================================
# MAIN LOOP
# ============================================================

print()
print("===================================")
print("VOICE + CAMERA + QWEN TTS READY")
print("Say 'quit' to exit.")
print("Examples:")
print("- What do you see?")
print("- Look ahead.")
print("- Describe the camera image.")
print("- Is there an obstacle?")
print("- Tell me a joke.")
print("===================================")

say("Voice camera assistant is ready.")

while True:
    user_text = listen()
    if not user_text:
        print("(nothing heard)")
        continue
    print("You:", user_text)

    if "quit" in user_text.lower() or "exit" in user_text.lower():
        say("Goodbye.")
        break
    try:
        if is_camera_question(user_text):
            say("Let me look.")
            image_path, error = capture_image()
            if error:
                say(error)
                continue
            reply = ask_qwen_vision(
                image_path=image_path,
                user_question=user_text
            )
            say(reply)

        else:
            reply = ask_qwen_text(user_text)
            say(reply)

    except Exception as e:
        print("ERROR:", e)
        say("Sorry, an error occurred.")