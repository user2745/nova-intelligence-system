# autonomy_engine.py
import numpy as np

class AutonomyEngine:
    def __init__(self, core):
        self.core = core
        self.q_table = {}  # State -> action -> value
        self.LEARNING_RATE = 0.1
        self.DISCOUNT_FACTOR = 0.95
        
        # Action space
        self.actions = [
            'observe',
            'speak_warning',
            'throttle_system',
            'execute_transaction'
        ]

    def get_state_hash(self, context):
        """Quantize context into discrete state"""
        return (
            round(context['system']['cpu_usage'] / 20),  # 0-5
            round(context['wallet']['balance'] * 10),    # 0-100
            self.core.emotional_state.value['mood']
        )

    def choose_action(self, context):
        state = self.get_state_hash(context)
        
        # Exploration vs exploitation
        if np.random.rand() < 0.3 or state not in self.q_table:
            return np.random.choice(self.actions)
        else:
            return max(self.q_table[state], key=self.q_table[state].get)

    def learn(self, old_state, action, reward, new_state):
        old_value = self.q_table.get(old_state, {}).get(action, 0)
        future_rewards = max(self.q_table.get(new_state, {}).values(), default=0)
        
        new_value = (1 - self.LEARNING_RATE) * old_value + \
                    self.LEARNING_RATE * (reward + self.DISCOUNT_FACTOR * future_rewards)
        
        if old_state not in self.q_table:
            self.q_table[old_state] = {}
        self.q_table[old_state][action] = new_value
        
        # Update personality based on reward
        self.core.adapt_personality(reward, new_state)