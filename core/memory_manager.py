# memory_manager.py
from datetime import datetime, time
import asyncio
import json
from utils.memory.questdb_memory import QuestDBMemoryManager  # Previous component
from dmus.ai_dmu import AIDMU  # Modified to handle memory processing

class NeuroMemoryManager:
    def __init__(self, mutable_context):
        self.storage = QuestDBMemoryManager(max_memory_hours=24)
        self.llm = AIDMU(model_name="deepthink-r1")
        self.context = mutable_context
        self.daily_summary = None
        self.sleep_time = time(3, 30)  # 3:30 AM default consolidation time
        self._scheduler_task = None
        
    async def initialize(self, nova_core):
        """Inject core reference and start daily scheduler"""
        await self.storage.initialize()
        self._scheduler_task = asyncio.create_task(self._daily_scheduler())

    async def record_thought(self, thought: str, context: dict):
        """Store a thought with full context snapshot"""
        await self.storage.insert("raw_thoughts", {
            "timestamp": datetime.utcnow(),
            "thought": thought,
            "context": json.dumps(context),
            "processed": False
        })

    async def _daily_scheduler(self):
        """Run consolidation at configured sleep time daily"""
        while True:
            now = datetime.now().time()
            if (now.hour == self.sleep_time.hour and 
                now.minute >= self.sleep_time.minute):
                
                await self.consolidate_memories()
                await asyncio.sleep(86300)  # Wait ~24 hours
            else:
                await asyncio.sleep(60)

    async def consolidate_memories(self):
        """End-of-day memory processing"""
        print("Nova: Beginning nightly memory consolidation...")
        
        # 1. Get unprocessed thoughts from last 24h
        raw_thoughts = await self.storage.query(
            "raw_thoughts",
            start=datetime.utcnow() - timedelta(hours=24),
            end=datetime.utcnow()
        )

        # 2. Generate LLM summary
        summary = await self._generate_summary(raw_thoughts)
        
        # 3. Store condensed memory
        await self.storage.insert("long_term_memory", {
            "timestamp": datetime.utcnow(),
            "summary": summary,
            "context_hash": hash(self.context.get_current_context())
        })

        # 4. Mark raw thoughts as processed
        await self._cleanup_raw_thoughts(raw_thoughts)
        
        print(f"Nova: Memory consolidation complete. Summary: {summary[:100]}...")

    async def _generate_summary(self, thoughts):
        """Use DeepThink to condense memories"""
        prompt = """Condense today's experiences into key learnings. Focus on:
- System performance patterns
- Decision effectiveness
- User interaction trends

Raw Thoughts:
{thoughts}"""

        return await self.llm.run(
            prompt.format(thoughts="\n".join(t["thought"] for t in thoughts))
        )

    async def _cleanup_raw_thoughts(self, thoughts):
        """Move processed thoughts to cold storage"""
        # Batch update processed flag
        for thought in thoughts:
            thought["processed"] = True
            await self.storage.insert("raw_thoughts", thought)
        
        # Flush to QuestDB
        await self.storage.graceful_shutdown()

# Modified AIDMU for memory integration
class AIDMUWithMemory(AIDMU):
    def __init__(self, memory_manager, **kwargs):
        super().__init__(**kwargs)
        self.memory = memory_manager

    async def run(self, context):
        """Generate thought and store in memory"""
        thought = await super().run(context)
        await self.memory.record_thought(thought, context)
        return thought