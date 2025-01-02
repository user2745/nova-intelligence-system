import asyncio
import pyttsx3
import speech_recognition as sr

class UserInputExecutor:
    """
    Executor for handling user input.
    """

    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def text(self):
        """
        type the user input.
        """
        return input("[You]: ")

    def speak(self, text):
        """
        Speak the given text.
        """
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """
        Listen for user input.
        """
        with self.microphone as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            print("Recognizing...")
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except Exception as e:
                return str(e)
    
    def get_user_input(self):
        """
        Get user input and return it as a string.
        """
        self.speak("Please say something.")
        user_input = self.text()
        return user_input
    
    @staticmethod
    async def run(self):
        """
        Run the user input executor.
        """
        try:
            executor = UserInputExecutor()
            user_input = executor.get_user_input()
            return user_input
        except Exception as e:
            return {"status": "error", "message": str(e)}   