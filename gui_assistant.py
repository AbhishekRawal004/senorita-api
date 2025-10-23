# gui_assistant.py
import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import pyttsx3
import os

from command_parser import CommandParser
from action_handler import ActionHandler

# ---------- Vosk Model Setup ----------
BASE_MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
SAMPLE_RATE = 16000

def find_vosk_model(base_dir):
    if not os.path.exists(base_dir):
        return None
    for root, dirs, files in os.walk(base_dir):
        if any(os.path.isdir(os.path.join(root, sub)) for sub in ("am", "conf", "graph")):
            return root
    return None

model_dir = find_vosk_model(BASE_MODELS_DIR)
if model_dir is None:
    print("Vosk model not found. Download & unzip into models/")
    exit(1)

model = Model(model_dir)
rec = KaldiRecognizer(model, SAMPLE_RATE)
q_audio = queue.Queue()
tts = pyttsx3.init()
parser = CommandParser()
actions = ActionHandler()

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Senorita Assistant")
root.geometry("500x400")

chat_area = scrolledtext.ScrolledText(root, state='disabled', wrap='word')
chat_area.pack(padx=10, pady=10, fill='both', expand=True)

entry_frame = tk.Frame(root)
entry_frame.pack(fill='x', padx=10, pady=5)

command_var = tk.StringVar()
entry_field = tk.Entry(entry_frame, textvariable=command_var)
entry_field.pack(side='left', fill='x', expand=True, padx=(0,5))

def speak(text):
    chat_area.config(state='normal')
    chat_area.insert(tk.END, "Assistant: " + text + "\n")
    chat_area.see(tk.END)
    chat_area.config(state='disabled')
    tts.say(text)
    tts.runAndWait()

def handle_command(text):
    chat_area.config(state='normal')
    chat_area.insert(tk.END, "You: " + text + "\n")
    chat_area.see(tk.END)
    chat_area.config(state='disabled')

    intent, slots = parser.parse(text.lower())
    actions.handle(intent, slots, speak)

def send_command():
    text = command_var.get().strip()
    if text:
        handle_command(text)
        command_var.set("")

entry_field.bind("<Return>", lambda e: send_command())

# ---------- Voice Recognition ----------
def callback(indata, frames, time, status):
    if status:
        print("Audio status:", status)
    q_audio.put(bytes(indata))

def listen_voice():
    speak("Listening...")
    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            while True:
                data = q_audio.get()
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    j = json.loads(res)
                    text = j.get("text", "")
                    if text:
                        handle_command(text)
                    break
    except Exception as e:
        speak("Audio error: " + str(e))

def start_voice_thread():
    t = threading.Thread(target=listen_voice, daemon=True)
    t.start()

mic_button = tk.Button(entry_frame, text="🎤", command=start_voice_thread)
mic_button.pack(side='right')

speak("Hello! I am ready. Type or speak a command.")

root.mainloop()
