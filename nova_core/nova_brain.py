# nova_core.py
from rx import operators as ops
from rx.subject import Subject, BehaviorSubject  
from .core_identity import CoreIdentityTraits  # Fixed import
from .llm_mafia import DeepThinkMafia  # Add missing import
from .intent_processing_engine import IntentProcessingEngine
import logging
import time

logging.basicConfig(level=logging.INFO)

class NovaBrain:
    def __init__(self, ucp):
        self.ucp = ucp
        self.identity = CoreIdentityTraits()
        self.llm = DeepThinkMafia(self.ucp, self.identity)
        self.memory = LongTermMemory()
        self.personality = EvolvingPersonality(self.identity, self.memory)
        self.decision_engine = MemoryDrivenDecision(self.memory)
        self.running = True

        # Subscribe to context updates
        # Decision loop
        self.ucp.context_stream.pipe(
            ops.throttle_first(1)
        ).subscribe(self.think)

        # Creating the parallel processes for the local ai's cognitive functions

        # Working memory streams
        self.memory_stream = Subject()
        self.intent_processing_stream = Subject()
        self.action_awareness_stream = Subject()
        self.fast_action_stream = Subject()
        self.goal_generation_stream = Subject()
        self.social_awarness_stream = Subject()

        # There are 8 components to the local ai's cognitive functions
        # Each of these components will be run in parallel, Proprioception, Goal, Working Memory, Short Term Memory, Long Term Memory, Social Awareness, Environment Detail, and Traits

        # These components are split into three levels of processing:
        # 1) the neural level
        # 2) the cognitive level
        # 3) the knowledge level

        # How it works, the streams act as buffers that transfer information between different modules
        # Production rules are stored in procedural memory

        # The Chunk is the basic unit of knowledge in declarative memory.  So cognititions produce chunks of knowledge ( aka a json with either a fact and/or instruction )
        # Instructions that refer to external states we call macro cognitions 
        # Instructions that refer to internal states we call meta cognitions
        # A meta cognition can be memory (learning, mnemonic devices, memory palace), reasoning ( science, logic math), physical ( sports, navy seal training, motor skills), or emotional ( CBT, self regulation, meditation)
        # Reference: https://www.youtube.com/watch?v=8LDrjpXnoeE&t=191s

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

    async def think(self, context):
        """Enhanced parallel context processing with Q-learning at the core."""
        try:
            # 1️⃣ PERCEPTION: Process incoming real-world data
            structured_context = await self.perception_engine.process_input(context)

            # 2️⃣ PARALLEL THINKING: Run reasoning, memory recall, and self-questioning
            parallel_results = await self.parallel_engine.run_parallel_thinking(structured_context)

            # 3️⃣ INTENT FORMATION: Filter and prioritize insights before execution
            selected_intent = await self.intent_processing_engine.process_intent(parallel_results)

            # 4️⃣ EXECUTION & LEARNING: Apply the selected intent and reinforce learning
            await self.temporal_memory.record_event("Nova", selected_intent)
            await self.memory_engine.record_experience("Context Processing", {"intent": selected_intent})

            print(f"🧠 Nova has processed context and executed intent: {selected_intent}")

        except Exception as e:
            print(f"Error processing context: {e}")