import requests

class AIDMU:
    def __init__(self, llm_url="http://localhost:11434/api/chat", model_name="phi3"):
        self.llm_url = llm_url
        self.model_name = model_name

    def run(self, context):
        prompt = f"""
        Context: {context}
        Task: Analyze the context and provide actionable advice in natural language.
        """
        try:
            response = requests.post(
                self.llm_url,
                json={"model": self.model_name, "messages": [{"role": "user", "content": prompt}], "stream": False},
            )
            response.raise_for_status()
            result = response.json()
            return result.get("completion", "No actionable insights.")
        except requests.RequestException as e:
            return f"AI Decision Error: {str(e)}"
