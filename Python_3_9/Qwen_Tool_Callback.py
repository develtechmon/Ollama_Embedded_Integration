import ollama

MODEL = "qwen3.5:4b"

client = ollama.Client(host="http://127.0.0.1:11434")

# The real function. ollama NEVER sees or introspects this — we call it ourselves.
def set_led(state: bool) -> str:
    print(f"   >>> [hardware would fire here] set_led({state})")
    return "ok"

# The catalog card you fill out by hand — handed straight to ollama as a dict.
# This is what sidesteps the pydantic introspection that crashes on 3.9.
TOOLS = [{
    "type": "function",
    "function": {
        "name": "set_led",
        "description": "Turn the ESP32 LED on or off.",
        "parameters": {
            "type": "object",
            "properties": {
                "state": {
                    "type": "boolean",
                    "description": "True to turn the LED on, False to turn it off.",
                },
            },
            "required": ["state"],
        },
    },
}]

# Because ollama no longer holds the function, YOU map name -> function.
DISPATCH = {"set_led": set_led}

messages = [{"role": "user", "content": "it's dark in here, switch the led on"}]

# think=False speeds it up; if your ollama client is old and rejects it, just delete that arg.
resp = client.chat(model=MODEL, messages=messages, tools=TOOLS, think=False)
print("tool_calls:", resp.message.tool_calls)

if resp.message.tool_calls:
    messages.append(resp.message)
    for call in resp.message.tool_calls:          # model DECIDES -> we EXECUTE
        fn = DISPATCH.get(call.function.name)
        result = fn(**call.function.arguments) if fn else f"unknown tool: {call.function.name}"
        messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})
    final = client.chat(model=MODEL, messages=messages, think=False)
    print("model says:", final.message.content)
else:
    print("!! NO tool call — the model just talked instead. That's the failure to watch for.")