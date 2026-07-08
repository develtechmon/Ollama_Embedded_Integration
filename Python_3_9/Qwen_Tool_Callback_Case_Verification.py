import ollama

MODEL = "qwen3.5:4b"

client = ollama.Client(host="http://127.0.0.1:11434")

def set_led(state: bool) -> str:
    return "ok"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "set_led",
        "description": "Turn the ESP32 LED on or off.",
        "parameters": {
            "type": "object",
            "properties": {
                "state": {"type": "boolean",
                          "description": "True to turn the LED on, False to turn it off."},
            },
            "required": ["state"],
        },
    },
}]

# expected: True/False = the state it SHOULD set; None = it must NOT call the tool at all
CASES = [
    ("switch the led on",                    True),
    ("turn the led off",                     False),
    ("can you flip on the led for me",       True),   # different phrasing
    ("it's too bright, turn the led off",    False),  # indirect
    ("what's the capital of France?",        None),   # <-- must stay silent
    ("tell me a short joke",                 None),   # <-- must stay silent
    ("is the led on right now?",             None),   # a question, not a command
]

passed = 0
for prompt, expected in CASES:
    resp = client.chat(model=MODEL,
                       messages=[{"role": "user", "content": prompt}],
                       tools=TOOLS, think=False)
    calls = resp.message.tool_calls or []
    if expected is None:
        ok = len(calls) == 0
        got = "silent" if ok else f"FIRED set_led({dict(calls[0].function.arguments)})"
    else:
        ok = (len(calls) == 1
              and calls[0].function.name == "set_led"
              and calls[0].function.arguments.get("state") == expected)
        got = f"set_led({dict(calls[0].function.arguments)})" if calls else "no call"
    passed += ok
    print(f"[{'PASS' if ok else 'FAIL'}] {prompt!r}")
    print(f"        want: {'silent' if expected is None else f'set_led({expected})'}   got: {got}")

print(f"\n{passed}/{len(CASES)} passed")