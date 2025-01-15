import numpy as np
import re
import time
import random
import signal
import importlib
import asyncio
import sys

from engines.system_context_engine import SystemContextEngine
from engines.time_context_engine import TimeContextAwarenessEngine

class NovaManager:
    """
    Manager class for the Nova system, responsible for managing context, decisions, and actions. 
    """
    def __init__(self, mutable_context, nova_registry):
        self.engines = {"SystemContextEngine": SystemContextEngine(), "TimeContextAwarenessEngine": TimeContextAwarenessEngine()} 
        self.context = mutable_context
        self.registry = nova_registry
        self.executors = []
        self.active_tasks = set()

    def save_state(self):
        pass

    def load_state(self):
        pass
   
    async def add_task(self, coro, name):
            task = asyncio.create_task(coro, name=name)
            self.active_tasks.add(task)
            task.add_done_callback(self.active_tasks.discard)
            print(f"Task {name} added.")
            return task

    async def monitor_system_stats(self):
        try:
            while True:  # Simulating continuous monitoring
                stats = self.engines["SystemContextEngine"].gather_context()
                self.context.update_context("CPU_usage", stats["cpu_usage"])
                self.context.update_context("GPU_usage", stats["gpu_usage"])
                self.context.update_context("memory_usage", stats["memory_usage"])
                self.context.update_context("disk_usage", stats["disk_usage"])
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("System stats monitoring task was cancelled.")
            raise
        finally:
            print("System stats monitoring task completed.")

    async def monitor_time_status(self):
        try:
            while True:  # Simulating continuous monitoring
                current_time = self.engines["TimeContextAwarenessEngine"].gather_context()
                self.context.update_context("time_of_day", current_time)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Time status monitoring task was cancelled.")
            raise
        finally:
            print("Time status monitoring task completed.")

    async def monitor_time_block_status(self):
        try:
            while True:
                time_block = self.enginers["TimeAwarenessEngine"].gather_context()
                self.context.update_context("time_block", time_block)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("System time block monitoring task was cancelled")
            raise
        finally:
            print("Systme time block monitoring completed")


    def get_tasks(self):
        return list(self.active_tasks)
    
    def run_tasks(self):
        # user_input_task = asyncio.create_task(self.handle_user_input())
        try:
            event_monitor_task = asyncio.create_task(self.monitor_system_stats())
            time_monitor_task = asyncio.create_task(self.monitor_time_status())
            self.active_tasks.add(event_monitor_task)  # Add task to active task set
            self.active_tasks.add(time_monitor_task)  # Add task to active task set
            time_monitor_task.add_done_callback(self.active_tasks.discard)  # Remove task when done
            event_monitor_task.add_done_callback(self.active_tasks.discard)  # Remove task when done
            return list(self.active_tasks)
        except Exception as e:
            event_monitor_task = print(f"Error creating event monitor task: {e}")
            []