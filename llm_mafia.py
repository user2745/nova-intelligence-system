# llm_mafia.py
from rx import operators as ops
import requests
import json

class DeepThinkMafia:
    def __init__(self, ucp):
        self.ucp = ucp
        self.model_name = "deepseek-llm"
        self.llm_endpoint = "http://localhost:11434/api/chat"

        # Subscribe only to chat commands with context
        self.ucp.command_stream.pipe(
            ops.filter(lambda cmd: cmd.get("action") == "chat"),
            ops.with_latest_from(self.ucp.context_stream),
            ops.map(lambda pair: (pair[0], pair[1]))
        ).subscribe(self._handle_chat)

    def _handle_chat(self, data):
        """Handle chat commands with real-time context"""
        command, context = data
        
        # Build context-aware prompt
        prompt = f"""
        [Nova System - Current Context]
        Time: {context.get('time', 'unknown')}
        CPU: {context.get('system', {}).get('cpu', '?')}%
        Memory: {context.get('system', {}).get('memory', '?')}%
        Wallet: {context.get('wallet', {}).get('balance', '?')} ETH

        [User Message]
        {command.get('content', '')}

        [Response Requirements]
        - Keep responses under 2 sentences
        - Reference system context where relevant
        - Be helpful and concise
        """

        try:
            # Get LLM response
            response = requests.post(
                self.llm_endpoint,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=5
            ).json()

            # Emit formatted response
            self.ucp.emit_response({
                "action": "chat_response",
                "session_id": command.get("session_id"),
                "content": response['message']['content'],
                "context": {
                    "timestamp": context.get('time'),
                    "system_stats": context.get('system')
                }
            })

        except Exception as e:
            self.ucp.emit_response({
                "action": "error",
                "message": f"Failed to process chat: {str(e)}"
            })