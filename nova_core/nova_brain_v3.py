import os
import asyncio
import time
import json
from nova_core.models.situational_model import SituationalAwareness
from nova_core.models.situational_model import SituationalModel
from nova_core.models.working_memory import WorkingMemory
from nova_core.models.declarative_memory import DeclarativeMemory
from nova_core.models.procedural_memory import ProceduralMemory
from nova_core.models.chain_of_thought import ChainOfThoughts
from datetime import datetime
from collections import defaultdict
import networkx as nx  # For graph-based declarative memory
from rx.subject import BehaviorSubject, Subject
import logging

logging.basicConfig(level=logging.INFO)

class NovaBrainV3:
    """The brain manages the cognitive cycle, sleep cycle, and three forms of memory: working, declarative and procedural."""
    def __init__(self, ucp):
        self.ucp = ucp
        self.running = True

        # Memory sets
        self.working_memory = WorkingMemory()
        self.declarative_memory = DeclarativeMemory()  # Graph-based memory
        self.procedural_memory = ProceduralMemory()      # For procedural knowledge

        # Cognitive Sets
        self.chain_of_thought = ChainOfThoughts(device_id="NovaCore")

        # Situational awareness
        self.situational_awareness = SituationalAwareness()

        # Initialize Key setups of the cognitive cycle
        self.context_stream = Subject()
        asyncio.create_task(self.cognitive_cycle())

    async def cognitive_cycle(self):
        """Main cognitive cycle running at ~50ms."""
        while self.running:
            start_time = time.time()

            # Step #1 - Perception
            # (implement perception logic here)

            # Step #2 - Processing/Decision-making
            # (implement processing logic here)

            # Maintain ~50ms cycle (SMM A4)
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0.05 - elapsed, 0))
    
    def select_action(self):
        wm = self.working_memory
        af = wm.get("affordances", [])
        # --- Exploration first ---
        if random.random() < 0.8:               # ε-greedy exploration
            return random.choice(af) if af else "idle"
        # --- Very small learned bias example ---
        for rule in self.procedural_memory["rules"]:
            if rule["condition"](wm): 
                return rule["action"]
        return "idle"