# llm_mafia.py
from rx import operators as ops
import requests  # For API calls to your LLM
import random
import json

class DeepThinkMafia:
    def __init__(self, ucp):
        self.ucp = ucp
        self.model_name = "deepseek-llm"
        self.llm_endpoints = [  
            # "http://deepthink-01:11434",  
            "http://localhost:11434/api/chat"  
        ]  
        # Subscribe to commands + context
        self.ucp.command_stream.pipe(
            ops.with_latest_from(self.ucp.context_stream),
            ops.map(lambda pair: {"command": pair[0], "context": pair[1]})
        ).subscribe(self._process_command)

    def _process_command(self, data):
        """Let the LLM decide the fate of the command."""
        command = data["command"]
        context = data["context"]

        # Build LLM prompt
        prompt = f"""
        [Nova System Decision]
        Command: {json.dumps(command)}
        Context: {json.dumps(context)}
        Should we execute this? If yes, format response as {{"action": "...", "params": {{}}}}
        """

        # Call DeepThink-r1 API (replace with actual API call)
        llm_response = self._call_llm(prompt)
        
        # Emit new action to the UCP
        self.ucp.emit_command(llm_response)

    def _call_llm(self, prompt: str):  
        chosen_llm = random.choice(self.llm_endpoints)  # Chaos load balancing
        try:
            response = requests.post(
                chosen_llm,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
            )
            response.raise_for_status()  # Ensure the request succeeded
            result = response.json()  # Parse the JSON response

            # Validate that the LLM's output matches the expected format
            if isinstance(result, dict) and "action" in result:
                return result
            else:
                print(f"⚠️ Invalid LLM response format: {result}")
                return {
                    "action": "error",
                    "params": {"message": "LLM response format invalid"}
                }

        except requests.exceptions.RequestException as e:
            print(f"💥 LLM request failed: {e}")
            return {
                "action": "error",
                "params": {"message": f"LLM request failed: {str(e)}"}
            }
    