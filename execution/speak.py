import time
import pyttsx3

def init_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    return engine

def say_time(engine):
    current_time = time.strftime("%I:%M %p")  # Format: e.g., "08:18 PM"
    engine.say(f"Hello sir, the time is {current_time}")
    engine.runAndWait()

def main():
    engine = init_tts()
    while True:
        say_time(engine)
        time.sleep(300)  # Wait 5 minutes (300 seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped by user")