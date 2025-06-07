class SelfObserver:
    """
    Quietly observes Nova's internal state over time,
    identifying shifts in memory, emotion, and cognition.
    Writes symbolic observations to declarative memory.
    """

    def __init__(self, nova_brain):
        self.brain = nova_brain
        self.last_emotional_state = self.brain.emotional_state.value.copy()
        self.last_action = None
        self.last_memory_snapshot = {}

    def observe(self):
        observations = []
        now = datetime.now()

        # 1. Emotional changes
        current_emotion = self.brain.emotional_state.value
        for key, current_value in current_emotion.items():
            previous_value = self.last_emotional_state.get(key)
            if current_value != previous_value:
                observations.append({
                    "type": "emotional_shift",
                    "dimension": key,
                    "from": previous_value,
                    "to": current_value,
                    "timestamp": now.isoformat()
                })
        self.last_emotional_state = current_emotion.copy()

        # 2. Action awareness
        current_action = self.brain.chain_of_thought[-1]["action"] if self.brain.chain_of_thought else None
        if current_action and current_action != self.last_action:
            observations.append({
                "type": "action_update",
                "action": current_action,
                "timestamp": now.isoformat()
            })
            self.last_action = current_action

        # 3. Memory size shift (symbolic)
        memory_delta = len(self.brain.working_memory) - len(self.last_memory_snapshot)
        if memory_delta != 0:
            observations.append({
                "type": "memory_growth",
                "delta": memory_delta,
                "timestamp": now.isoformat()
            })
        self.last_memory_snapshot = self.brain.working_memory.copy()

        # 4. Record all observations in declarative memory
        for obs in observations:
            node_id = f"observation_{now.timestamp()}_{len(obs)}"
            self.brain.declarative_memory.add_node(node_id, **obs)

        return observations
