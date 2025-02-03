import numpy as np
import sounddevice as sd
from tts import TTS
from nova_core.core_identity import CoreIdentity  # Get Nova's emotional state

class NovaSpeechSynthesis:
    def __init__(self, ucp, core: CoreIdentity, model_name="tts_models/en/ljspeech/glow-tts"):
        self.tts = TTS(model_name)
        self.core_identity = core  # Access Nova’s mood & personality
        self.ucp = ucp
        # Subscribe to Nova's emotional state
        self.ucp.context_stream.subscribe(self._handle_speaking)


    def _handle_speaking(self, data):
        try:
            if data.get("action") == "speak":
                self.speak(data.get("content", ""))
            elif data.get("action") == "stop_speaking":
                self.stop_speaking()
        except Exception as e:
            print(f"Failed to handle speaking: {str(e)}")

    def get_emotional_tone(self):
        """Modify Nova's speaking style based on her emotional state."""
        mood = self.core_identity.emotional_state.value["mood"]
        
        if mood == "neutral":
            return {"speed": 1.0, "pitch": 1.0}
        elif mood == "stressed":
            return {"speed": 1.2, "pitch": 1.1}
        elif mood == "panicked":
            return {"speed": 1.4, "pitch": 1.3}
        elif mood == "playful":
            return {"speed": 0.9, "pitch": 0.95}
        else:
            return {"speed": 1.0, "pitch": 1.0}

    def speak(self, text):
        """Generate and play Nova's voice in real-time."""
        tone = self.get_emotional_tone()
        
        print(f"🎙️ Nova speaking (Mood: {self.core_identity.emotional_state.value['mood']})...")
        
        # Generate speech
        audio_array = self.tts.tts(
            text=text,
            speed=tone["speed"],
            pitch=tone["pitch"]
        )
        
        # Play speech
        sd.play(audio_array, samplerate=22050)
        sd.wait()  # Block until audio is finished playing

    def stop_speaking(self):
        """Immediately stops Nova's speech playback."""
        sd.stop()
        print("⏹️ Nova stopped speaking.")
