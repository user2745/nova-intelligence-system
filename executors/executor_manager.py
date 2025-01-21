import os
import json
import asyncio
import logging
from collections import defaultdict
from typing import Callable, Dict, Any
from executors.blockchain_transaction_executor import BlockchainTransactionExecutor
from engines.modules.blockchain_wallet import BlockchainWallet

logging.basicConfig(level=logging.INFO)

class ExecutorManager:
    """
    Manager class for executing tasks via registered modules, similar to NovaManager.
    """
    def __init__(self, mutable_context, executor_registry, loop):
        self.task_queue = asyncio.PriorityQueue()
        self.ucp_command_queue = asyncio.Queue()  # Queue for UCP commands
        self.context = mutable_context
        self.modules = {}
        self.loop = loop  # Main asyncio loop
        self.registry = executor_registry
        self.task_results = defaultdict(list)
        self.active_tasks = set()
        # Do I wanna move this setup to the registry yes/no?
        wallet = BlockchainWallet(
            rpc_url="https://mainnet.base.org",
            private_key = os.environ.get("WALLET_PRIVATE_KEY", "")
        )
        blockchain_executor = BlockchainTransactionExecutor(wallet)
        self.register_module("blockchain_transaction_executor", blockchain_executor)


    def register_module(self, module_name: str, module: Callable):
        """Register a module to be used for task execution."""
        self.modules[module_name] = module

    async def add_task(self, priority: int, module_name: str, task_data: dict):
        """
        Add a module task to the PriorityQueue using the unified format.
        """
        try:
            task_data = {
                "priority": priority,
                "type": "task",  # Task type
                "content": {
                    "module_name": module_name,
                    "task_data": task_data,
                },
            }
            await self.task_queue.put((task_data["priority"], task_data))  # Add task with priority
            logging.info(f"Task added to queue: {module_name} with priority {priority}")
        except Exception as e:
            logging.error(f"[ExecutorManager] Error adding module task: {e}")

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
    
    async def execute_transaction(to_address, amount):
        """
        Add a blockchain transaction task to the executor manager.
        """
        task_data = {"to_address": to_address, "amount": amount}
        result = await executor_manager.add_task(1, "blockchain_transaction_executor", task_data)
        return result


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
    
    async def add_ucp_command(self, command, topic):
        """
        Add a UCP command to the PriorityQueue using the unified format.
        """
        try:
            task_data = {
                "priority": 0,
                "type": "ucp",  # Task type
                "content": {
                    "command": command,
                    "topic": topic,
                },
            }
            await self.task_queue.put((task_data["priority"], task_data))  # Add task with priority
            logging.info(f"[ExecutorManager] Added UCP command: {command}")
        except Exception as e:
            logging.error(f"[ExecutorManager] Error adding UCP command: {e}")


    async def process_ucp_commands(self):
        """
        Process all tasks (UCP and module tasks) from the PriorityQueue.
        """
        try:
            while not self.task_queue.empty():
                _, task_data = await self.task_queue.get()  # Get task data
                task_type = task_data["type"]  # Determine task type

                # Handle UCP commands
                if task_type == "ucp":
                    command = task_data["content"]["command"]
                    topic = task_data["content"]["topic"]
                    logging.info(f"[ExecutorManager] Processing UCP command: {command} from topic: {topic}")

                    if command["action"] == "send_funds":
                        to_address = command.get("to_address")
                        amount = command.get("amount")
                        if not to_address or not isinstance(amount, (int, float)):
                            logging.error("[ExecutorManager] Invalid send_funds command: Missing 'to_address' or invalid 'amount'.")
                            continue

                        # Convert amount to WEI and add to task queue
                        task_data = {"to_address": to_address, "amount": int(amount * 10**18)}
                        await self.add_task(1, "blockchain_transaction_executor", task_data)
                        logging.info(f"[ExecutorManager] Task added to send {amount} ETH to {to_address}")

                    elif command["action"] == "ping":
                        response_topic = f"ucl/status/{topic.split('/')[-1]}"
                        self.context.ucp_client.publish(
                            response_topic,
                            json.dumps({"status": "success", "response": "pong"})
                        )
                        logging.info("[ExecutorManager] Responded to ping.")

                    else:
                        logging.warning(f"[ExecutorManager] Unknown UCP action: {command['action']}")

                # Handle module tasks
                elif task_type == "task":
                    module_name = task_data["content"]["module_name"]
                    task_data = task_data["content"]["task_data"]
                    logging.info(f"[ExecutorManager] Executing module task: {module_name} with data: {task_data}")
                    await self.execute_task(module_name, task_data)

                else:
                    logging.error(f"[ExecutorManager] Unknown task type: {task_type}")

        except Exception as e:
            logging.error(f"[ExecutorManager] Error in process_ucp_commands: {e}")

    async def execute_actions(self):
        """
        Continuously process all tasks from the unified queue.
        """
        try:
            while True:
                await self.process_ucp_commands()  # Process all tasks in the unified queue
                await asyncio.sleep(0.1)  # Prevent busy looping
        except Exception as e:
            logging.error(f"Error in ExecutorManager execution loop: {e}")
        finally:
            logging.info("ExecutorManager shutting down.")

