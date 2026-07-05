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