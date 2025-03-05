# core_identity.py
import os
import json
from datetime import datetime
import numpy as np
from rx.subject import BehaviorSubject
from sklearn.preprocessing import normalize

class CoreIdentityTraits:
    def __init__(self):
        # Dynamic personality matrix (traits x contexts)

        self.identity_file = "core-identity.json"
        self.personality = BehaviorSubject(self._load_identity())
        
        # Emotional state
        self.emotional_state = BehaviorSubject({
            'stress': 0.0,
            'focus_energy': 0.5,
            'mood': 'neutral'
        })
        
        # Memory systems
        self.episodic_memory = []  # Time-stamped events
        self.semantic_graph = {}  # Concept relationships

    def adapt_personality(self, reward: float, context: dict):
        """Reinforcement learning-based trait adjustment"""
        current = self.personality.value
        adjustment = np.random.rand(len(current)) * reward - 0.1
        new_traits = normalize([list(current.values()) + adjustment])[0]
        self.personality.on_next(dict(zip(current.keys(), new_traits)))

    def record_episode(self, event: dict):
        """Store events with emotional context"""
        self.episodic_memory.append({
            'timestamp': datetime.now(),
            'event': event,
            'emotional_state': self.emotional_state.value.copy()
        })

    def _load_identity(self):
        """Load state from a local file if it exists, otherwise return default."""
        if os.path.exists(self.identity_file):
            try:
                with open(self.identity_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass  # Corrupt file, return default

        return {}  # Default state

    def calculate_concept_relationship(self, concept_a: str, concept_b: str):
        """Build semantic relationships"""
        if concept_a not in self.semantic_graph:
            self.semantic_graph[concept_a] = {}
        self.semantic_graph[concept_a][concept_b] = \
            self.semantic_graph[concept_a].get(concept_b, 0) + 1