import numpy as np
import random
import json
import os

class QLearningEngine:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.2, memory_file="q_table.json"):
        self.actions = actions
        self.learning_rate = learning_rate  # Alpha: How much new information overrides old
        self.discount_factor = discount_factor  # Gamma: Importance of future rewards
        self.exploration_rate = exploration_rate  # Epsilon: Probability of random action selection
        self.memory_file = memory_file

        self.q_table = self._load_q_table()  # Load past learning

    def _load_q_table(self):
        """Load Q-table from storage or initialize a new one."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as file:
                return json.load(file)
        return {}

    def _save_q_table(self):
        """Save Q-table to memory file."""
        with open(self.memory_file, "w") as file:
            json.dump(self.q_table, file, indent=4)

    def get_q_value(self, state, action):
        """Retrieve Q-value for a given state-action pair."""
        return self.q_table.get(state, {}).get(action, 0.0)

    def choose_action(self, state):
        """Select an action using an epsilon-greedy policy."""
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.actions)  # Explore (random action)
        
        # Exploit: Choose best known action
        q_values = {action: self.get_q_value(state, action) for action in self.actions}
        best_action = max(q_values, key=q_values.get)
        return best_action

    def update_q_value(self, state, action, reward, next_state):
        """Update the Q-table based on experience."""
        old_value = self.get_q_value(state, action)
        future_rewards = max([self.get_q_value(next_state, a) for a in self.actions], default=0)
        
        # Q-learning formula: Q(s, a) = Q(s, a) + α * [reward + γ * max Q(s', a') - Q(s, a)]
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * future_rewards - old_value)
        
        # Store new Q-value
        self.q_table.setdefault(state, {})[action] = new_value
        self._save_q_table()
