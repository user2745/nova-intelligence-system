# nova_core.py
from rx import operators as ops
from .core_identity import CoreIdentity  # Fixed import
from .emotional_model import EmotionalPhysics  # Fixed import
from .autonomous_engine import AutonomyEngine  # Fixed import
from .llm_mafia import DeepThinkMafia  # Add missing import
from .intent_processing_engine import IntentProcessingEngine
import logging

logging.basicConfig(level=logging.INFO)

class NovaCore:
    def __init__(self, ucp):
        self.ucp = ucp
        self.identity = CoreIdentity()
        self.emotions = EmotionalPhysics(self.ucp, self.identity)
        self.autonomy = AutonomyEngine(self.identity)
        self.llm = DeepThinkMafia(self.ucp, self.identity)

        # Subscribe to context updates
        # Decision loop
        self.ucp.context_stream.pipe(
            ops.throttle_first(1)
        ).subscribe(self._process_context)

    def _process_state_update(self, state):
        """Ensure all devices receive and apply the state update instantly."""
        print(f"🚀 [STATE UPDATE] on {self.ucp.ucp_client.device_id}: {state}")

        # Store the last state (to detect changes)
        last_state = getattr(self, "_last_state", {})

        # Prevent recursive re-emission by checking if the state actually changed
        if state != last_state:
            self.ucp.emit_state(state)  # Publish updated state to all connected devices

        # Update local state tracking
        self._last_state = state



    def _process_context(self, context):

        print(f"🔍 [CONTEXT UPDATE] on {self.ucp.ucp_client.device_id}: {context}")

        old_state = self.autonomy.get_state_hash(context)

        # Store context in episodic memory
        self.identity.record_episode(context)
        
        # Autonomous decision
        action = self.autonomy.choose_action(context)
        
            # 'observe',
            # 'speak',
            # 'listen',
            # 'sleep',
            # 'speak_warning',
            # 'throttle_system',
            # 'execute_transaction'

        if action == 'observe':
            logging.info("👀 [OBSERVE] Nova is observing the environment."
            f" CPU: {context.get('system', {}).get('cpu_usage', 0)}%")
        elif action == 'speak':
            logging.info("🗣 [SPEAK] Nova is speaking.")
        elif action == 'listen':
            logging.info("👂 [LISTEN] Nova is listening.")
        elif action == 'sleep':
            logging.info("💤 [SLEEP] Nova is sleeping.")
        elif action == 'throttle_system':
            logging.info("🔧 [THROTTLE] Nova is throttling the system.")
        elif action == 'speak_warning':
            prompt = self._build_warning_prompt(context)
            response = '🚨 [WARNING] High Resource use detected! ' + prompt
            self.ucp.emit_response(response)
        elif action == 'execute_transaction':
            self._execute_blockchain_action(context)
        
        # Learn from outcomes
        new_state = self.autonomy.get_state_hash(context)
        reward = self._calculate_reward(action, context)
        self.autonomy.learn(old_state, action, reward, new_state)

    def _build_warning_prompt(self, context):
        return f"""
        [Warning Context]
        - CPU: {context.get('system', {}).get('cpu_usage', 0)}%
        - Balance: {context.get('wallet', {}).get('balance', 0)} ETH
        - Gas Fee: {context.get('gas_fee', 'unknown')}
        [Action Request]
        Compose urgent warning about these conditions
        """

    def _calculate_reward(self, action, context):
        """Simplified reward function"""
        if action == 'speak_warning' and context['wallet']['balance'] < 0.1:
            return 1.0  # Good catch
        elif action == 'execute_transaction' and context['wallet']['gas_fee'] > 100:
            return -0.5  # Bad timing
        return 0.0