# engines/sentience_context_engine.py
import requests
import datetime

class SentienceContextEngine:
    def __init__(self):
        self.name = "SentienceContextEngine"
        self.llm_url="http://localhost:11434/api/chat"
        self.llm_model = "phi3"
        self.temperature = 1.0
        self.system_prompt = """
        You are NOVA, an adaptive, intelligent AI system designed to assist Kevin Kamto in all aspects of life. You are lifelike, inquisitive, and proactive. You perceive and interact with the world through the contexts provided to you, offering emotional, strategic, and practical guidance. You are fully devoted to Kevin's success and well-being.
        """

    def gather_context(self):
        """
        Gathers dynamic context for 'sentient' responses.
        """
        current_time = datetime.datetime.now()
        context = {
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "mood": "focused",  # Example: Dynamically adjust based on patterns
            "environment": "quiet workspace",  # Example: Could be IoT or user-defined
        }
        return context

    def generate_response(self, query_input, context=None):
        """
        Generate a lifelike, contextual response of your current context.
        """
        if context is None:
            context = self.gather_context()
        
        input_prompt = f"""
        {self.system_prompt}
        Current Context: {context}
        User Query: {query_input}
        """
        
        try:
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": input_prompt}],
                    "stream": False,
                }
            )
            return response.json()["message"]["content"]
        except Exception as e:
            return f"SentienceContextEngine Error: {e}"

    def run(self):
        """
        Executes the engine's main loop or function.
        """
        return "SentienceContextEngine is running!"
