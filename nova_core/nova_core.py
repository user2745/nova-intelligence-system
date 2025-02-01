# nova_core.py
from rx import operators as ops
from .core_identity import CoreIdentity  # Fixed import
from .emotional_model import EmotionalPhysics  # Fixed import
from .autonomous_engine import AutonomyEngine  # Fixed import
from .llm_mafia import DeepThinkMafia  # Add missing import

class NovaCore:
    def __init__(self, ucp):
        self.ucp = ucp
        self.identity = CoreIdentity()
        self.emotions = EmotionalPhysics(self.ucp, self.identity)
        self.autonomy = AutonomyEngine(self.identity)
        self.llm = DeepThinkMafia(self.ucp, self.identity)

        self.ucp.state_stream.subscribe(self._process_state_update)
        
        # Decision loop
        self.ucp.context_stream.pipe(
            ops.throttle_first(1)
        ).subscribe(self._process_context)

    def _process_state_update(self, state):
        """React to distributed state updates."""
        print("State updated:", state)
        # Handle any specific logic based on updated state.

    def _process_context(self, context):

        old_state = self.autonomy.get_state_hash(context)

        # Store context in episodic memory
        self.identity.record_episode(context)
        
        # Autonomous decision
        action = self.autonomy.choose_action(context)
        
        if action == 'speak_warning':
            prompt = self._build_warning_prompt(context)
            response = "The system is under heavy load. Please consider reducing your workload."
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

    def _execute_blockchain_action(self, context):
        # Placeholder for blockchain execution
        pass

    def _calculate_reward(self, action, context):
        """Simplified reward function"""
        if action == 'speak_warning' and context['wallet']['balance'] < 0.1:
            return 1.0  # Good catch
        elif action == 'execute_transaction' and context['wallet']['gas_fee'] > 100:
            return -0.5  # Bad timing
        return 0.0