# questdb_memory.py
from datetime import datetime, timedelta
import asyncio
from utils.questdb import QuestDBConnector  # Your existing QuestDB class

class QuestDBMemoryManager:
    def __init__(self, max_memory_hours=2, flush_interval=300):
        self.qdb = QuestDBConnector()
        self.memory_cache = {}  # {table_name: {"data": deque(), "schema": [...]}}
        self.max_memory_hours = max_memory_hours
        self.flush_interval = flush_interval
        self.flush_task = None
        self.lock = asyncio.Lock()

    async def initialize(self):
        """Start background flush task"""
        self.flush_task = asyncio.create_task(self._auto_flush())

    async def insert(self, table: str, data: dict):
        """Insert data into memory cache with schema validation"""
        async with self.lock:
            if table not in self.memory_cache:
                # Initialize new table cache with schema detection
                self.memory_cache[table] = {
                    "data": [],
                    "schema": list(data.keys()),
                    "created_at": datetime.utcnow()
                }
            
            # Validate schema consistency
            if list(data.keys()) != self.memory_cache[table]["schema"]:
                raise ValueError(f"Schema mismatch for table {table}")

            self.memory_cache[table]["data"].append({
                **data,
                "timestamp": datetime.utcnow()
            })

    async def query(self, table: str, start: datetime, end: datetime):
        """Query combined memory and QuestDB data"""
        async with self.lock:
            # 1. Check memory cache
            mem_results = []
            if table in self.memory_cache:
                mem_results = [
                    row for row in self.memory_cache[table]["data"]
                    if start <= row["timestamp"] <= end
                ]

            # 2. Query QuestDB for older data
            qdb_results = await self.qdb.query_time_range(table, start, end)

            return sorted(mem_results + qdb_results, key=lambda x: x["timestamp"])

    async def _auto_flush(self):
        """Periodically flush old data to QuestDB"""
        while True:
            await asyncio.sleep(self.flush_interval)
            async with self.lock:
                cutoff = datetime.utcnow() - timedelta(hours=self.max_memory_hours)
                
                for table in list(self.memory_cache.keys()):
                    # Split data into old and current
                    old_data = [
                        row for row in self.memory_cache[table]["data"]
                        if row["timestamp"] < cutoff
                    ]
                    
                    current_data = [
                        row for row in self.memory_cache[table]["data"]
                        if row["timestamp"] >= cutoff
                    ]

                    # Flush old data to QuestDB
                    if old_data:
                        await self._flush_to_qdb(table, old_data)
                        self.memory_cache[table]["data"] = current_data

                    # Remove empty tables
                    if not current_data:
                        del self.memory_cache[table]

    async def _flush_to_qdb(self, table: str, data: list):
        """Batch insert into QuestDB"""
        columns = self.memory_cache[table]["schema"]
        records = [
            tuple(row[col] for col in columns)
            for row in data
        ]
        
        await self.qdb.batch_insert(table, columns, records)

    async def graceful_shutdown(self):
        """Flush all data on shutdown"""
        if self.flush_task:
            self.flush_task.cancel()
            
        async with self.lock:
            for table in self.memory_cache:
                await self._flush_to_qdb(table, self.memory_cache[table]["data"])