import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, Any

logging.basicConfig(level=logging.INFO)

class ExecutorManager:
    """
    Manager class for executing tasks via registered modules, similar to NovaManager.
    """
    def __init__(self, mutable_context, executor_registry):
        self.task_queue = asyncio.PriorityQueue()
        self.context = mutable_context
        self.modules = {}
        self.registry = executor_registry
        self.task_results = defaultdict(list)
        self.active_tasks = set()

    def register_module(self, module_name: str, module: Callable):
        """Register a module to be used for task execution."""
        self.modules[module_name] = module

    async def add_task(self, priority: int, module_name: str, task_data: dict):
        """Add a task to the queue with a given priority."""
        await self.task_queue.put((priority, module_name, task_data))
        logging.info(f"Task added to queue: {module_name} with priority {priority}")

    async def execute_task(self, module_name: str, task_data: dict) -> Dict[str, Any]:
        """Execute a task using the specified module."""
        module = self.modules.get(module_name)
        if not module:
            logging.error(f"Module {module_name} not found!")
            return {"status": "error", "message": f"Module {module_name} not registered."}

        try:
            result = await module.run(task_data)
            self.task_results[module_name].append(result)
            return result
        except Exception as e:
            logging.error(f"Execution failed for {module_name}: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def process_task(self):
        """Process a single task from the queue."""
        while not self.task_queue.empty():
            priority, module_name, task_data = await self.task_queue.get()
            logging.info(f"Processing task: {module_name} with priority {priority}")
            result = await self.execute_task(module_name, task_data)
            logging.info(f"Task result: {result}")

    async def monitor_system_stats(self):
        """Monitor system stats and trigger alerts or tasks based on conditions."""
        logging.info("Monitoring system stats...")
        try:
            while True:
                # Simulate system stats monitoring
                stats = {
                    "cpu_usage": self.context.get_context["CPU_usage"],  # This will be dynamically changed during stress testing
                    "gpu_usage": self.context.get_context["GPU_usage"],
                    "memory_usage": self.context.get_context["memory_usage"],
                    "disk_usage": self.context.get_context["disk_usage"],
                }
                logging.info(f"System Stats: {stats}")

                # React to high CPU usage
                if stats["cpu_usage"] > 80:
                    logging.warning("High CPU usage detected! Adding a mitigation task...")
                    await self.add_task(1, "mitigation_module", {"action": "reduce_load"})

                await asyncio.sleep(1)  # Check system stats every second
        except asyncio.CancelledError:
            logging.info("System stats monitoring task was cancelled.")
            raise


    async def execute_actions(self):
        """Continuously process tasks in the priority queue."""
        try:

            # Continously collect user input
            
            # TODO: Implement user input

            # Continuously process tasks in the queue
            while True:
                await self.process_task()
                await asyncio.sleep(0.1)  # Small delay to avoid busy looping
        except Exception as e:
            logging.error(f"Error in ExecutorManager run loop: {e}")
        finally:
            logging.info("ExecutorManager shutting down.")
