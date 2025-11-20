#!/usr/bin/env python3
"""
Speak Agent using Piper-TTS HTTP Server
----------------------------------------
Converts text -> audio using Piper TTS HTTP server.

Integrates with LangChain 1.x / LangGraph tools.
"""

import requests
from pathlib import Path
from langchain.tools import tool


# Piper TTS HTTP server configuration
PIPER_SERVER_URL = "http://localhost:5000"
OUTPUT_DIR = Path("audio_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


@tool
def speak(text: str, voice: str = "en_US-lessac-medium") -> str:
    """
    Convert input text into speech using Piper-TTS HTTP server.
    
    Args:
        text: The text to synthesize
        voice: Voice to use (optional), defaults to en_US-lessac-medium
    
    Returns the path to the generated WAV file.
    """
    if not text.strip():
        return "Error: text is empty."

    output_path = OUTPUT_DIR / "speech.wav"

    try:
        # POST request to Piper TTS server
        response = requests.post(
            PIPER_SERVER_URL,
            headers={"Content-Type": "application/json"},
            json={"text": text},
            timeout=30
        )
        
        if response.status_code == 200:
            # Save the WAV file
            with open(output_path, "wb") as f:
                f.write(response.content)
            return f"Audio generated: {output_path}"
        else:
            return f"Error: Server returned status {response.status_code}"

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Piper TTS server. Is it running on port 5000?"
    except requests.exceptions.Timeout:
        return "Error: Request to Piper TTS server timed out."
    except Exception as e:
        return f"Speak agent error: {e}"
