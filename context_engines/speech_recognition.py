import queue
import sys
import json
import asyncio
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class SpeechRecognition:
    def __init__(self, ucp, model_path="vosk-model-en-us-0.22-lgraph"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()
        self.ucp = ucp  # Initialize Nova's communication system
        self.interrupted = False  # Flag to detect interruptions
        asyncio.create_task(self.recognize())

    def _audio_callback(self, indata, frames, time, status):
        """Callback function that continuously streams audio input."""
        if status:
            print(f"Audio Status: {status}", file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def recognize(self):
        """Real-time voice recognition loop."""
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                               channels=1, callback=self._audio_callback):
            print("🎙️ Nova is listening... (Say something)")
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"🗣 Recognized: {text}")
                        self.process_command(text)

    def process_command(self, text):
        """Handles recognized speech commands and sends them to Nova's UCP."""
        if "stop" in text.lower():
            print("🛑 Nova interrupted.")
            self.interrupted = True  # Mark as interrupted
            self.ucp.emit_command({"action": "interrupt", "content": "User interrupted Nova."})
        else:
            print(f"✅ Sending to Nova: {text}")
            self.ucp.emit_command({"action": "chat", "content": text})