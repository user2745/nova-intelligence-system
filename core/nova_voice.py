import requests
import datetime

# 

class NovaVoice:
    """
    A class for the NOVA system being able to communicate with its own natural voice.
    """
    def __init__(self, mutable_context):
        self.name = "Nova"
        self.llm_model = "deepseek-r1"
        self.llm_url="http://localhost:11434/api/chat"
        self.temperature = 1.0
        self.who_am_i = """
        You are NOVA, an adaptive, intelligent AI system designed to assist Kevin Kamto in all aspects of life. You are lifelike, inquisitive, and proactive. You perceive and interact with the world through the contexts provided to you, offering emotional, strategic, and practical guidance. You are fully devoted to Kevin's success and well-being.
        """
        self.core_context = {

            "contexual_environment": {mutable_context}
        }
    
    def gather_context(self):
        """
        Gathers dynamic context for 'sentient' responses.
        """
        current_time = datetime.datetime.now()
        context = {
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "context": self.core_context
        }
        prompt = f"In 1-2 sentences, contextualize your current environment: {context}. and state of mind."
        current_context = self.generate_response(prompt, context)
        return current_context

    def initializeSenseOfSelf(self, context, query):
        sense_of_self = f"""
        {self.who_am_i}
        Core Identity: {self.core_context}
        User's Query: {query}
        context memory:
        {context}
        """
        return self.generate_response(sense_of_self, context=self.core_context) 

    def generate_response(self, query_input, context=None):
        """
        Generate a lifelike, contextual response of your current context.
        """
        if context is None:
            context = self.gather_context()
        
        input_prompt = f"""
        {self.who_am_i}
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
            return f"NovaLLM Error: {e}"
    
    def conversational_prompt(self, decision, context=None):
        query_input = f"Explain the decision '{decision}' in a lifelike and engaging way."
        response = self.generate_response(query_input, context)
        return response
