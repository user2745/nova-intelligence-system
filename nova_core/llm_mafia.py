# llm_mafia.py
from rx import operators as ops
import requests
import json
from nova_core.core_identity import CoreIdentity

class DeepThinkMafia:
    def __init__(self, ucp, core: CoreIdentity):
        self.ucp = ucp
        self.core = core
        self.model_name = "deepseek-llm"
        self.llm_endpoint = "http://localhost:11434/api/chat"

        # Subscribe to chat commands with core identity context
        self.ucp.command_stream.pipe(
            ops.filter(lambda cmd: cmd.get("action") == "chat"),
            ops.with_latest_from(self.ucp.context_stream),
            ops.map(lambda pair: (pair[0], pair[1]))
        ).subscribe(self._handle_chat)

    def _build_prompt(self, command, context):
        traits = self.core.personality.value
        mood = self.core.emotional_state.value['mood']
        day_phase = context.get('day_phase')
        time = context.get('time')
        return f"""
        You are Nova, an advanced AI with a complex personality matrix, created by Kevin Kamto. You are currently in a {mood} mood.
        [Your (Nova) Current Configuration]
        Your Personality Traits: {traits}
        Right now, your emotional state is: {mood}
        Focus: {context.get('focus', 'general')}

        [Contextual Information]
        It is currently {day_phase} ({time}).
        System Information: {context.get('system')},
        Wallet Information: {context.get('wallet')}
        
        [Response Requirements]
        - The Contextual information is the real life contextual environment
        - your current configuration is your personality and emotional state
        - your response should take all this information into account, including your current mood: {mood}
        - Never respond with your thought process or thinking, only as Nova and only generate a response to Kevin Kamto's Input
        - Never break character
        
        [Kevin Kamto's Input]
        {command.get('content', '')}
        """

    def generate(self, prompt):
        response = requests.post(
            self.llm_endpoint,
            json={
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=5
        ).json()

        return response

    def _handle_chat(self, data):
        """Handle chat with core identity integration"""
        command, context = data
        print(f"🤖 Nova processing chat: {command}")
        try:
            # Ensure we have at least a minimal context if none is provided
            if not context:
                context = {
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'day_phase': 'day',
                    'system': {},
                    'wallet': {},
                    'focus': 'general'
                }
            
            # Build identity-aware prompt
            prompt = self._build_prompt(command, context)
            print(f"🔍 Generated prompt: {prompt}")  # Debug log
            
            # Get LLM response
            try:
                response = self.generate(prompt)
                print(f"📝 LLM Response: {response}")  # Debug log
                
                if not response or 'message' not in response:
                    raise Exception("Invalid response from LLM")

                # Store interaction in memory
                self.core.record_episode(f"User: {command.get('content', '')}\nNova: {response['message']['content']}")

                # Emit response
                self.ucp.emit_response({
                    "action": "chat_response",
                    "session_id": command.get("session_id"),
                    "content": response['message']['content'],
                    "context": {
                        "timestamp": context.get('time'),
                        "system_stats": context.get('system'),
                        "mood": self.core.emotional_state.value['mood']
                    }
                })

            except requests.exceptions.RequestException as e:
                print(f"❌ LLM request failed: {str(e)}")
                raise

        except Exception as e:
            print(f"❌ Error in chat handling: {str(e)}")
            self.ucp.emit_response({
                "action": "error",
                "session_id": command.get("session_id"),
                "message": f"Failed to process chat: {str(e)}"
            })