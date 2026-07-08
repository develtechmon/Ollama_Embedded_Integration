## Getting Started

We're going to run `ollama` locally in our `window`. In my case, i'm using window 11 and using ollama local. Please follow this step

### Step 1: Download and install ollama

Go to `ollama` website and copy the link in your `powersheel` terminal
```
irm https://ollama.com/install.ps1 | iex
```

### Step 2: Pull the model and download it local machine

In my case, i prefer to use this model because it's a multimodal that support `vision`, `tools` and `thinking`. Which is suitable for robotic project.
Now let's download
```
 ollama pull qwen3.5:4b
```

And in terminal, let's run this in `CLI`
```
ollama run qwen3.5:4b
```

If you don't want to see the thinking process, you can do the following
```
/set nothink
```

and you can set this again later
```
/set think
```

## Step 3: Install python packages

In my version, i'm using `python 3.9`. You can install the following packages which help later
```
pip install faster-whisper sounddevice
pip install ollama
pip install piper-tts
python -m piper.download_voices en_US-lessac-medium
pip install pyserial
```

## Step 3: Script Definition

For this development it's divided into several categories

`whisper` - This script read the text from microphone as user text. Basically, it converts audio to text. This is used by Human to AI

`Piper` - This script will perform text to voice especially used by AI to speak to us

`Tool Callback` - This script define the tool integration with our hardware.

`Voice Chat` - Is an example of script that enable us to speak with VLM


## Communcation Method

There are several way to conenct `ollama` with `esp32` which already inside this project. 
The method are as :
```
1. Using Serial - ESp32 connect G14 laptop using USB
2. Using Wifi Protocol
```


If you want to conenct using `WIFi` please following the following approach in `G14` to ensure the port is accessible
For this to work you have to implement the following 1st, otherwise the communcation between ESp32 to Ollama in G14 laptop wont work.

## Please follow this Step
1. Right-click Ollama in the system tray → Quit (fully quit, don't just close window).
2. Start menu → search "environment variables" → Edit environment variables for your account.
3. New… → Name: OLLAMA_HOST, Value: 0.0.0.0 → OK.
4. New… again → Name: OLLAMA_ORIGINS, Value: * → OK.
5. Relaunch Ollama from Start menu.
6. Find your G14's LAN IP: ipconfig in cmd → look for IPv4 Address under your Wi-Fi adapter (something like 192.168.x.x, or if on hotspot, 10.68.x.x).
7. Sanity test — from your phone's browser on the same WiFi, visit http://<G14_IP>:11434. If you see "Ollama is running", the network side is solved. If you don't, no ESP32 code will save you — fix that first.
   ```
   From browse type this:
   http://10.68.173.137:11434/
   ```

   You will see this output:
   ```
   Ollama is running
   ```
   
## Client ESP32

If you're using ESP32 as a client, you can refer to following code. In short, you'll chat with the `ollama` directly using `serial monitor` of arduino and you will see response from 
ollama running in G14.

1. upload the `ollama_wifi_chat_with_esp32.ino` code attached in this project. Please ensure the `OLLAMA_URL` ip address match to G14 IP4 address as in step `7`.
2. Once done upload, change the Serial Monitor to `New Line` to see the behaviour.
3. From serial monitor, type the chat you want and then press enter. You should see the respond immediately.

## Client Local G14

Since we've setup the `OLLAMA_HOST` and `OLLAMA_ORIGINS`, we have to call the model locally by specifiying this line in our python code.

1. Go inside `python_3_9` and select any of the script such as `Voice_Chat.py` and then please ensure you set this `client = ollama.Client(host="http://127.0.0.1:11434")`
Otherwise the code wont work.
2. And then run the Script as it's

