import os
import asyncio
import time
import json
from datetime import datetime
from collections import defaultdict
import networkx as nx  # For graph-based declarative memory
from rx.subject import BehaviorSubject, Subject
import logging

logging.basicConfig(level=logging.INFO)

class NovaBrainV3:
    """ The brain manages the cognitive cycle, sleep cycle, and three forms of memory: working, declarative and procedural. """
    def __init__(self, ucp):
        self.ucp = ucp
        self.running = True
        
        # Memory sets
        self.working_memory = {}
        self.declarative_memory = nx.Graph()
        self.procedural_memory = {
            "rules": [],  # If-then rules
            "skills": {},  # Complex action sequences
            "habits": []  # Highly reinforced behaviors
        }

        # Cognitive Sets
        self.chain_of_thought = []
        self.emotional_state = BehaviorSubject({
            'stress': 0.0,
            'focus_energy': 0.8,
            'mood': 'neutral'
        })        
        # Initialize Key setps of the cognitive cycle
        self.context_stream = Subject()
        self.initialize_memory()
        asyncio.create_task(self.cognitive_cycle())

    def initialize_memory(self):
        # Add initial declarative memories
        self.declarative_memory.add_node("coffee_preference", 
                                    success_rate=0.5,
                                    last_updated=datetime.now())
    

        # Add initial procedural rules
        self.procedural_memory.append({
            "condition": lambda wm: wm.get("hour", 0) == 8 and wm.get("user_present", False),
            "action": "suggest_coffee",
            "weight": 0.8  # For reinforcement learning (SMM C3a)
        })
    
    async def cognitive_cycle(self):
        """Main cognitive cycle running at ~50ms. """
        while self.running:
            try:
                start_time = time.time()
                # Step 1: Update working memory with context (SMM D1)
                context = self.ucp.context_stream.value
                self.working_memory.update(context)

                # Step 2: Include previous thought as reference (chain-of-thought)
                previous_thought = self.chain_of_thought[-1] if self.chain_of_thought else None
                if previous_thought:
                    self.working_memory["previous_thought"] = previous_thought

                # Step 3: Select action using procedural memory (SMM B3)
                action = self.select_action()

                # Step 4: Execute action and get outcome
                outcome = await self.execute_action(action)

                # Step 5: Record thought in chain-of-thought ledger
                thought_record = {
                    "timestamp": datetime.now().isoformat(),
                    "working_memory": self.working_memory.copy(),
                    "action": action,
                    "outcome": outcome,
                    "priority_weight": self.calculate_priority(outcome),  # For pruning
                    "emotional_state": self.emotional_state.value.copy()
                }
                self.chain_of_thought.append(thought_record)
                logging.info(f"Thought recorded: {thought_record}")

                # Step 6: Learn from outcome (SMM C1-C5)
                self.learn_from_outcome(thought_record)

                # Step 7: Check if sleep is needed
                if await self.should_enter_sleep():
                    await self.enter_sleep_cycle()

                # Maintain ~50ms cycle (SMM A4)
                elapsed = time.time() - start_time
                await asyncio.sleep(max(0.05 - elapsed, 0))
            except Exception as e:
                logging.error(f"Cognitive cycle error: {str(e)}", exc_info=True)
                # Optional: update emotional state
                self.emotional_state.on_next({
                    **self.emotional_state.value,
                    "stress": min(self.emotional_state.value["stress"] + 0.2, 1.0),
                    "mood": "distressed"
                })
                await asyncio.sleep(1)  # Brief pause before retrying



    def select_action(self):
        """Select an action based on consciousness and procedural memory."""

        return "idle"  # Default action if no rules match

    async def execute_action(self, action):
        """Execute the selected action and return the outcome."""
        
        return {"success": False, "feedback": "No action taken"}

        """Generate hypothetical scenarios and rules during sleep (Dreaming Phase)."""
        # Example: Dream about suggesting tea instead of coffee on weekends
        if "previous_thought" in self.working_memory:
            last_thought = self.working_memory["previous_thought"]
            if last_thought["action"] == "suggest_coffee" and not last_thought["outcome"]["success"]:
                # Simulate a new scenario
                dream_thought = {
                    "timestamp": datetime.now().isoformat(),
                    "working_memory": {"hour": 8, "day_phase": "weekend", "user_present": True},
                    "action": "suggest_tea",
                    "outcome": {"success": True, "feedback": "Dream scenario: Tea suggested"},
                    "priority_weight": 0.5,
                    "emotional_state": {"stress": 0.0, "mood": "playful"}
                }
                self.chain_of_thought.append(dream_thought)
                logging.info(f"Dreamed up: {dream_thought}")

                # Add a tentative procedural rule
                self.procedural_memory.append({
                    "condition": lambda wm: wm.get("hour", 0) == 8 and wm.get("day_phase", "") == "weekend",
                    "action": "suggest_tea",
                    "weight": 0.5  # Tentative, to be refined with real feedback
                })