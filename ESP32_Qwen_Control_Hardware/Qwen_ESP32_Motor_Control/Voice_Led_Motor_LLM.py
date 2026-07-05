import io
import wave
import json
import time
import serial
import ollama
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from piper import PiperVoice

# ============================================================
# ESP32 CONNECTION
# ============================================================

COM_PORT = "COM9"
BAUDRATE = 115200

esp = serial.Serial(
    COM_PORT,
    BAUDRATE,
    timeout=2
)

time.sleep(2)
esp.reset_input_buffer()
esp.write(b"PING\n")
reply = esp.readline().decode().strip()
print("Link Check:", reply)

if reply != "PONG":
    print("WARNING: ESP32 handshake failed")

# ============================================================
# AI MODELS
# ============================================================

MODEL = "qwen3.5:4b"
SR = 16000
print("Loading Whisper...")

whisper = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded")
print("Loading Piper...")

voice = PiperVoice.load(
    "en_US-lessac-medium.onnx"
)

print("Piper loaded")

# ============================================================
# HARDWARE CONTROL FUNCTIONS
# ============================================================
def send_command(cmd: str) -> str:
    esp.write((cmd + "\n").encode())
    result = esp.readline().decode().strip()
    if not result:
        result = "NO_RESPONSE"
    print("ESP32:", result)
    return result

# ------------------------------------------------------------
# LED
# ------------------------------------------------------------

def set_led(state: bool) -> str:
    if state:
        return send_command("LED:1")
    else:
        return send_command("LED:0")
# ------------------------------------------------------------
# MOTOR
# ------------------------------------------------------------

def move_motor(direction: str,
               pulses: int = 330) -> str:
    direction = direction.lower()
    if direction == "forward":
        return send_command(
            f"MOTOR:FWD:{pulses}"
        )

    elif direction == "backward":
        return send_command(
            f"MOTOR:REV:{pulses}"
        )

    else:
        return "INVALID_DIRECTION"

# ------------------------------------------------------------
# STOP MOTOR
# ------------------------------------------------------------
def stop_motor() -> str:
    return send_command(
        "MOTOR:STOP"
    )

# ------------------------------------------------------------
# STATUS
# ------------------------------------------------------------
def get_status() -> str:
    return send_command(
        "STATUS"
    )

# ============================================================
# TOOL DEFINITIONS
# ============================================================
TOOLS = [
{
    "type": "function",
    "function":
    {
        "name": "set_led",

        "description":
        "Turn LED on or off",

        "parameters":
        {
            "type": "object",

            "properties":
            {
                "state":
                {
                    "type": "boolean",
                    "description":
                    "true = on, false = off"
                }
            },

            "required":
            [
                "state"
            ]
        }
    }
},

{
    "type": "function",
    "function":
    {
        "name": "move_motor",

        "description":
        "Move motor using encoder position control",

        "parameters":
        {
            "type": "object",

            "properties":
            {
                "direction":
                {
                    "type": "string",

                    "enum":
                    [
                        "forward",
                        "backward"
                    ]
                },

                "pulses":
                {
                    "type": "integer",

                    "description":
                    "encoder target pulses"
                }
            },

            "required":
            [
                "direction"
            ]
        }
    }
},

{
    "type": "function",
    "function":
    {
        "name": "stop_motor",

        "description":
        "Immediately stop the motor",

        "parameters":
        {
            "type": "object",
            "properties": {}
        }
    }
},

{
    "type": "function",
    "function":
    {
        "name": "get_status",

        "description":
        "Get status from ESP32",

        "parameters":
        {
            "type": "object",
            "properties": {}
        }
    }
}
]

# ============================================================
# TOOL DISPATCH TABLE
# ============================================================
DISPATCH = {
    "set_led": set_led,
    "move_motor": move_motor,
    "stop_motor": stop_motor,
    "get_status": get_status
}


# ============================================================
# SPEECH TO TEXT
# ============================================================
def listen(seconds=5):
    input("\n[Press ENTER and speak] ")
    audio = sd.rec(
        int(seconds * SR),
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
# TEXT TO SPEECH
# ============================================================
def say(text):
    print("Assistant:", text)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
    buf.seek(0)
    data, sr = sf.read(buf)
    sd.play(data, sr)
    sd.wait()

# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You control an ESP32 robot.

Hardware:

1. LED
2. Encoder-controlled DC motor

Available tools:

set_led(state)

move_motor(direction, pulses)

stop_motor()

get_status()

Rules:

Turn on LED
-> set_led(True)

Turn off LED
-> set_led(False)

Move forward
-> move_motor("forward",330)

Move backward
-> move_motor("backward",330)

Move forward 2 revolutions
-> move_motor("forward",660)

Move backward 2 revolutions
-> move_motor("backward",660)

Half revolution
-> 165 pulses

Stop motor
-> stop_motor()

Use tools whenever a hardware action is requested.
"""

# ============================================================
# MAIN LOOP
# ============================================================
print()
print("===================================")
print("VOICE ROBOT READY")
print("Say 'quit' to exit")
print("===================================")


while True:
    cmd = listen()
    if not cmd:
        print("(nothing heard)")
        continue
    print()
    print("You:", cmd)

    if "quit" in cmd.lower():
        say("Goodbye")
        break

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "user",
            "content": cmd
        }
    ]

    try:
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            think=False
        )

        if response.message.tool_calls:
            messages.append(response.message)
            for call in response.message.tool_calls:
                name = call.function.name
                arguments = dict(call.function.arguments)

                print()
                print("Tool:", name)
                print("Args:", arguments)

                function = DISPATCH.get(name)

                if function:
                    result = function(**arguments)
                else:
                    result = "UNKNOWN_TOOL"
                messages.append(
                    {
                        "role": "tool",
                        "tool_name": name,
                        "content": str(result)
                    }
                )

            final = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                think=False
            )

            say(
                final.message.content
                or "Command completed."
            )

        else:            
            say(
                response.message.content
                or "I did not understand."
            )

    except Exception as e:
        print()
        print("ERROR:", e)
        say(
            "An error occurred."
        )