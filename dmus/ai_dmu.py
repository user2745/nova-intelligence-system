# ai_dmu.py
import aiohttp 

class AIDMU:
    def __init__(self, llm_url="http://localhost:11434/api/chat", model_name="deepthink-r1"):
        self.llm_url = llm_url
        self.model_name = model_name
        self.system_prompt = ("You are Nova's decision core. Analyze system context and propose actions. "
                            "Format: 'THOUGHT: <analysis> ACTION: <concrete action>'")

    async def run(self, context):
        """Async LLM query"""
        prompt = f"{self.system_prompt}\nContext: {context}\nTask: Propose one action."
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.llm_url,
                    json={
                        "model": self.model_name,
                        "messages": [{
                            "role": "user", 
                            "content": prompt
                        }],
                        "stream": False
                    }
                ) as response:
                    result = await response.json()
                    return result.get("message", {}).get("content", "No decision")
        except Exception as e:
            return f"Decision Error: {str(e)}"