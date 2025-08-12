import json
import aiohttp
import asyncio
import time
import logging
from rx.subject import Subject

class NovaBrainV4:
    """
    The brain manages the cognitive cycle, sleep cycle, and three forms of memory:
    working, declarative and procedural. This version runs a continuous conscious loop,
    processing perception, evaluating rules, invoking LLM inferences, and emitting actions.
    """
    def __init__(self, ucp: Subject, working_memory, declarative_memory,
                 procedural_memory, situational_awareness, chain_of_thought,
                 real_time_queue):
        self.ucp = ucp
        self.running = True
        logging.info(f"[Brain] Initializing NovaBrainV4... {self.running}")

        # Memory modules
        self.working_memory = working_memory
        self.declarative_memory = declarative_memory
        self.procedural_memory = procedural_memory
        self.situational_awareness = situational_awareness
        self.chain_of_thought = chain_of_thought

        # Input stream
        self.real_time_queue = real_time_queue

        # High-level cognitive processes
        

        # Low-level cognitive processes
        

        # Subscribe to context updates
        self.ucp.subscribe(self._on_context_event)

    def _on_context_event(self, event: dict):
        """
        Handle incoming context: update memories and enqueue thought blocks.
        Called immediately on every perception or command event.
        """
        payload = event

        # 1. Update Working Memory
        try:
            self.working_memory.write(payload)
        except Exception as e:
            logging.warning(f"WorkingMemory update failed: {e}")

        # 2. Log to Declarative Memory
        try:
            self.declarative_memory.add_episode(payload)
        except Exception as e:
            logging.warning(f"DeclarativeMemory add_episode failed: {e}")

        # 3. Update Situational Model
        try:
            self.situational_awareness.add_event(name="external_context", payload=payload)
            logging.info(f"SituationalModel updated with event: {payload}.  Current state: {self.situational_awareness.current_situation}")
        except Exception as e:
            logging.warning(f"SituationalModel merge_event failed: {e}")

        # 4. Enqueue Thought Block
        try:
            self.chain_of_thought.add_thought({
                'timestamp': time.time(),
                'thought': payload
            })
        except Exception as e:
            logging.warning(f"ChainOfThought add_thought failed: {e}")

    async def cognitive_cycle(self):
        """
        Main conscious loop running at ~50ms intervals.
        Processes queued thought blocks, applies rules, calls LLMs, and emits actions.
        """
        logging.info("[Brain] Starting cognitive cycle...")
        count = 0
        while self.running:
            cycle_start = time.time()
            logging.info(f"[Brain] Cognitive cycle iteration {count}")
            count += 1
            # Step 1: Fetch next thought block, if any
            try:
                thought = self.chain_of_thought.next_block()
                logging.info(f"[Brain] Processing thought block: {thought.index} at {thought.timestamp}")
            except Exception as e:
                logging.debug("[Brain] No thought block available.")

            # Step 2: Process real-time events
            while not self.real_time_queue.is_empty():
                event = await self.real_time_queue.dequeue()
                logging.info(f"[Brain] Processing real-time event: {event}")
                self._on_context_event(event)

            # Step 3: Apply real-time decision making

            # Step 4: Emit actions based on processed events

            # Step 5: Cleanup data 

            # Maintain cycle timing
            elapsed = time.time() - cycle_start
            await asyncio.sleep(max(0.05 - elapsed, 0))

    async def shutdown(self):
        """Stop the cognitive loop cleanly."""
        self.running = False

# Instantiate and integrate NovaBrainV4 in CoreModule when ready
