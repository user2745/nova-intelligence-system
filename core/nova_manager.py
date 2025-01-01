import numpy as np
import re
import time
import random
import signal
import importlib
import asyncio
import sys

from engines.context_awareness_engine import ContextAwarenessEngine

class NovaManager:
    """
    Manager class for the Nova system, responsible for managing context, insights, and events. 
    """
    def __init__(self, mutable_context, nova_registry):
        self.engines = {"ContextAwarenessEngine": ContextAwarenessEngine()}
        self.context = mutable_context
        self.registry = nova_registry
        self.dmus = []
        self.executors = []
        self.active_tasks = set()

    def save_state(self):
        pass

    def load_state(self):
        pass
   
    async def schedule_task(self, coro, name):
            task = asyncio.create_task(coro, name=name)
            self.active_tasks.add(task)
            task.add_done_callback(self.active_tasks.discard)
            return task

    def run_engines(self):
        """
        Run all loaded engines.
        """
        for engine in self.engines.values():
            engine.run()
        print("Engines running.")
    
    def stop_engines(self):
        """
        Stop all running engines.
        """
        for engine in self.engines.values():
            engine.stop()
        print("Engines stopped.")

    async def monitor_system_stats(self):
        print("Monitoring system stats...")
        try:
            while True:  # Simulating continuous monitoring
                stats = self.engines["ContextAwarenessEngine"].gather_context()
                print(stats)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("System stats monitoring task was cancelled.")
            raise
        finally:
            print("System stats monitoring task completed.")

    def print_context(self, key, value):
        print(f"Context updated: {key} -> {value}")
    

    def get_tasks(self):
        return list(self.active_tasks)

    def run_tasks(self):
        # user_input_task = asyncio.create_task(self.handle_user_input())
        try:
            event_monitor_task = asyncio.create_task(self.monitor_system_stats())
            self.active_tasks.add(event_monitor_task)  # Add task to active task set
            event_monitor_task.add_done_callback(self.active_tasks.discard)  # Remove task when done
            return list(self.active_tasks)
        except Exception as e:
            event_monitor_task = print(f"Error creating event monitor task: {e}")
            []