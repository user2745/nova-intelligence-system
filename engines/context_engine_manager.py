import asyncio
import sys

from engines.wallet_context_engine import WalletContextEngine
from engines.user_context_engine import UserContextEngine

class ContextEngineManager:
    def __init__(self, mutable_context,  context_registry):
        self.engines = {"WalletContextEngine": WalletContextEngine(), "UserContextEngine": UserContextEngine()}
        self.context = mutable_context
        self.active_tasks = set()
        self.registry = context_registry
    
    async def monitor_wallet_status(self):
        try:
            while True:
                wallet_status = self.engines["WalletContextEngine"].gather_context()
                self.context.update_context("wallet_status", wallet_status)
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            print("Wallet status monitoring task was cancelled.")
            raise
        finally:
            print("Wallet status monitoring task completed.")

    async def add_task(self, coro, name):
            task = asyncio.create_task(coro, name=name)
            self.active_tasks.add(task)
            task.add_done_callback(self.active_tasks.discard)
            print(f"Task {name} added.")
            return task

    def get_tasks(self):
        # Return all active tasks
        return list(self.active_tasks)

    async def run_tasks(self):
        try:
            wallet_status_task = asyncio.create_task(self.monitor_wallet_status())

            # Add tasks to the active set
            self.active_tasks.update([ wallet_status_task])

            # Add cleanup callbacks
            for task in self.active_tasks:
                task.add_done_callback(self.active_tasks.discard)

            return asyncio.gather(*self.active_tasks)  # Gather all tasks to execute concurrently
        except Exception as e:
            print(f"Error running context engine tasks: {e}")
            return []