import re
import datetime
import random
import signal
import importlib
import asyncio
import sys
from core.context.mutable_context import MutableContext
from core.nova_registry import NovaRegistry
from core.nova_manager import NovaManager
from core.nova_voice import NovaVoice

class NovaCore:
    """
    Core orchestrator for the Nova Intelligence System.
    Responsible for querying engines, making decisions, and executing actions.
    """

    def __init__(self, ImmutableContext):
        self.immutable_context = ImmutableContext
        self.mutable_context = None
        self.manager = None
        self.running = False

    def initialize(self):
        """
        Initialize the Nova system by setting up signal handlers.
        """
        print("[Core] Initializing the NOVA Intelligence System...")
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.graceful_shutdown()))
        print("Signal handlers set up successfully.")

        # Loading the initial context
        print("[Core] Loading initial context...")
        self.mutable_context = MutableContext(self.immutable_context)

        # Record startup event in context
        startup_entry = {
            "startup_time": datetime.datetime.now().isoformat(),
            "version": "1.0",  # Replace with your system's version
            "state": "initialized"
        }
        self.mutable_context.update_context("last_startup", startup_entry)

        # Initialize the registry
        print("[Core] Initializing the registry...")
        novaRegistry = NovaRegistry()

        # Loading the context & registry into the Manager
        print("[Core] Initializing the Nova Manager...")
        self.manager = NovaManager(self.mutable_context, novaRegistry);
        print("[Core] Nova Manager initialized");

        print("[Core] Initializing the Nova Voice with the contexual environment...")
        self.voice = NovaVoice(self.mutable_context)
        print("[Core] Nova Voice initialized");

        print("[Core] Speaking to Nova Voice...")
        print("[Core] Hello Nova!")
        nova_greeting = self.voice.initializeSenseOfSelf(self.mutable_context, "Hello, Nova!")
        print(nova_greeting)

        print("[Core] Nova is ready for operation.")
        self.mutable_context.freeze()
        self.running = True


    def shutdown_signal_handler(self, signum, frame):
        """
        Handles shutdown signals (SIGINT, SIGTERM) for graceful shutdown.
        """
        print("\n [Core] Shutdown signal received. Shutting down Nova gracefully...")
        self.running = False
        asyncio.create_task(self.graceful_shutdown())


    async def graceful_shutdown(self):
        """
        Gracefully shut down Nova by cancelling all active tasks and cleaning up resources.
        """
        print("[Core] Initializing graceful shutdown ...")
        tasks = list(self.manager.active_tasks)

        print(f"Cancelling {len(tasks)} tasks...")

        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print(f"Task {task.get_name()} has been cancelled.")

        print("All tasks cancelled. Saving memory state.")
        try:
            self.manager.save_state()
            self.mutable_context.freeze()
        except Exception as e:
            print(f"Error saving memory state: {e}")

        print("[Core] Nova has been shut down successfully. Goodbye!")
        sys.exit(0)

    async def run(self):
        try:
            print(f"Core: [{datetime.datetime.now()}] Nova is now running... [{self.running}]")
            tasks = self.manager.run_tasks()
            print(f"Running tasks: {tasks}")
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("[Core] Run loop cancelled.")
        except Exception as e:
            print(f"[Core] Run loop error: {e}")
        finally:
            await self.graceful_shutdown()
