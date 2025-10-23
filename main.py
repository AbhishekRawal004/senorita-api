# main.py
import queue
import sounddevice as sd
import sys
import json
from vosk import Model, KaldiRecognizer
import pyttsx3
import os
from command_parser import CommandParser
from action_handler import ActionHandler

SAMPLE_RATE = 16000

# ---------- Auto-detect Vosk model folder and load it ----------
BASE_MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

def find_vosk_model(base_dir):
    # search recursively for a folder that contains 'am' or 'conf' or 'graph'
    if not os.path.exists(base_dir):
        return None
    for root, dirs, files in os.walk(base_dir):
        if any(os.path.isdir(os.path.join(root, sub)) for sub in ("am", "conf", "graph")):
            return root
    return None

model_dir = find_vosk_model(BASE_MODELS_DIR)
print("Base models dir:", BASE_MODELS_DIR)
if model_dir is None:
    print("Could not find a Vosk model inside the 'models/' folder.")
    print("Please download & unzip a Vosk model inside the models/ directory.")
    sys.exit(1)

print("Using Vosk model at:", model_dir)

try:
    model = Model(model_dir)
    print("Vosk model loaded OK.")
except Exception as e:
    print("Failed to create Vosk model. Exception:", repr(e))
    print("Directory listing of model folder (first entries):")
    try:
        for i, entry in enumerate(sorted(os.listdir(model_dir))[:200]):
            print(" ", entry)
            if i > 200:
                break
    except Exception as ex:
        print("  (Could not list directory contents):", ex)
    sys.exit(1)
# ----------------------------------------------------------------

rec = KaldiRecognizer(model, SAMPLE_RATE)

q = queue.Queue()
tts = pyttsx3.init()
parser = CommandParser()
actions = ActionHandler()

def speak(text: str):
    print("Assistant:", text)
    tts.say(text)
    tts.runAndWait()

def callback(indata, frames, time, status):
    if status:
        print("Audio status:", status, file=sys.stderr)
    # ensure we put raw bytes (sounddevice gives a numpy buffer)
    q.put(bytes(indata))

def listen_and_recognize():
    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            print("Listening... (say something)")
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    j = json.loads(res)
                    text = j.get("text", "")
                    return text
                # Optionally check partial results:
                # partial = json.loads(rec.PartialResult()).get("partial", "")
                # if partial:
                #     print("Partial:", partial)
    except Exception as e:
        print("Audio input error:", e)
        raise

def main_loop():
    speak("Hello, how can I help you?")
    while True:
        try:
            text = listen_and_recognize()
            if not text:
                continue
            print("You said:", text)
            t = text.lower()
            if any(w in t for w in ("exit", "stop", "bye", "quit")):
                speak("Goodbye!")
                break

            intent, slots = parser.parse(t)
            actions.handle(intent, slots, speak)

        except KeyboardInterrupt:
            print("\nStopping.")
            break
        except Exception as e:
            print("Error:", e)
            speak("I encountered an error. Check the console.")

if __name__ == "__main__":
    main_loop()
