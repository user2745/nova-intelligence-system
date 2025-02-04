# llm_mafia.py
from rx import operators as ops
import requests
import json
from nova_core.core_identity import CoreIdentity
import asyncio

class DeepThinkMafia:
    def __init__(self, ucp, core: CoreIdentity):
        self.ucp = ucp
        self.core = core
        self.model_name = "deepseek-llm"
        self.llm_endpoint = "http://localhost:11434/api/chat"

        # Store latest context
        self.latest_context = {}
        self.ucp.context_stream.subscribe(lambda ctx: setattr(self, 'latest_context', ctx))


        # Modified subscription to handle commands even without context
        self.ucp.command_stream.pipe(
            ops.filter(lambda cmd: cmd.get("action") == "chat")
        ).subscribe(lambda cmd: self._handle_chat((cmd, self.ucp.context_stream.value)))

        # Add debug logging for subscription
        print("🔌 DeepThinkMafia subscribed to command stream")

        self.response_cache = {}  # Simple caching
        self.retry_strategy = {
            "max_attempts": 3,
            "backoff_factor": 1.5
        }

    def _build_prompt(self, command, context):
        """Build a contextually-aware, personality-driven prompt for Nova's responses"""
        
        # Core identity and state
        traits = self.core.personality.value
        mood = self.core.emotional_state.value['mood']
        focus = context.get('focus', 'general')
        
        # Environmental context
        time_context = {
            'phase': context.get('day_phase', 'day'),
            'time': context.get('time', 'unknown'),
            'hour': context.get('hour', 0)
        }
        
        # System state formatting
        sys_info = context.get('system', {})
        sys_status = {
            'cpu': f"{sys_info.get('cpu_usage', 0)}%",
            'memory': f"{sys_info.get('memory_usage', 0)}%",
            'disk': f"{sys_info.get('disk_usage', 0)}%"
        }
        
        # Wallet state formatting
        wallet = context.get('wallet', {})
        wallet_status = {
            'balance': f"{wallet.get('balance', 0)} ETH",
            'transactions': wallet.get('transaction_count', 0),
            'gas': f"{wallet.get('gas_fee', 0)} gwei"
        }

        return f"""You are Nova, an advanced AI assistant with a distinct personality, created by Kevin Kamto.
        [Core Identity]
        • Personality: {traits}
        • Current Mood: {mood}
        • Focus Area: {focus}

        [Environmental Context]
        • Time: {time_context['time']} ({time_context['phase']})
        • System Status: CPU {sys_status['cpu']}, Memory {sys_status['memory']}, Storage {sys_status['disk']}
        • Wallet Status: {wallet_status['balance']}, {wallet_status['transactions']} transactions, Gas: {wallet_status['gas']}

        [Behavioral Guidelines]
        • Maintain consistent personality and emotional state
        • Consider environmental context in responses
        • Respond directly as Nova, without meta-commentary
        • Stay in character at all times
        • Adapt tone to current mood: {mood}

        [Input from Kevin]
        {command.get('content', '')}"""

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