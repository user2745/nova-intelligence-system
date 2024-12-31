import re
import time
import random
import signal
import importlib
import asyncio
import sys
from core.nova_registry import NovaRegistry
from core.nova_manager import NovaManager
from core.feedback_loop import FeedbackLoop

from engines.weather_engine import WeatherEngine
from engines.sentience_context_engine import SentienceContextEngine

def to_camel_case(value):
    """
    Convert a string to camel case.
    Example: "test_engine" -> "TestEngine"
    """
    words = re.split(r'[_\s]', value)
    return ''.join(word.capitalize() for word in words)

class NovaCore:
    """
    Core orchestrator for the Nova Intelligence System.
    Responsible for querying engines, making decisions, and executing actions.
    """

    def __init__(self):
        self.registry = NovaRegistry()  # Manages all contextual engines
        self.voice = self.registry.get_voice()  # Manages the system's voice
        self.manager = NovaManager()  # Manages the system's memory
        self.feedback = FeedbackLoop()   # Monitors and logs system performance
        self.sentience_engine = SentienceContextEngine()
        self.weather_engine = WeatherEngine()
        self.running = True

    def initialize(self):
        """
        Initialize the Nova system by setting up signal handlers.
        """
        print("Initializing the Navigational Omni Virtual Assistant (NOVA) Intelligence System...")
        signal.signal(signal.SIGINT, self.shutdown_signal_handler)
        signal.signal(signal.SIGTERM, self.shutdown_signal_handler)
        print("Signal handlers set up successfully.")
        # Initializing the internal voice
        print("Initializing the internal voice...")
        wakeup_message =  f"""
            Wake up Nova! Once you gather all relevant information show you understand
             and internalized your identity by generating an extremely short, less than 2 stentence response to this query.
            """
        isNovaAwake = self.voice.initializeSenseOfSelf(self.manager.get_last_session(), wakeup_message)
        print(f"{isNovaAwake}")

        # Add Sentience Context Engine to the registry
        self.registry.add_engine(self.sentience_engine.name, "engines.sentience_context_engine")
        print(f"{self.sentience_engine.name} loaded and initialized.")
        # Add Weather Context Engine to the registry
        self.registry.add_engine(self.weather_engine.name, "engines.weather_engine");
        print(f"{self.weather_engine.name} loaded and initialized.")
        # Enabling cognition feedback loop
        


    def shutdown_signal_handler(self, signum, frame):
        """
        Handles shutdown signals (SIGINT, SIGTERM) for graceful shutdown.
        """
        print("\nShutdown signal received. Shutting down Nova gracefully...")
        self.running = False
        asyncio.create_task(self.graceful_shutdown())


    async def graceful_shutdown(self):
        """
        Gracefully shut down Nova by cancelling all active tasks and cleaning up resources.
        """
        print("Shutting down Nova gracefully...")

        # Get all tasks except the current one
        current_task = asyncio.current_task()
        tasks = [t for t in asyncio.all_tasks() if t is not current_task]
        print(f"Cancelling {len(tasks)} tasks...")

        for task in tasks:
            task.cancel()  # Request task cancellation

        # Gather tasks with a timeout to prevent infinite loops
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5)
        except asyncio.TimeoutError:
            print("Timeout: Not all tasks could be cancelled in time.")
        except asyncio.CancelledError:
            print("Tasks cancelled.")
        except Exception as e:
            print(f"Unexpected error during shutdown: {e}")

        print("All tasks cancelled or timed out. Saving memory state.")
        try:
            self.manager.save_state()
            print("Memory state saved.")
        except Exception as e:
            print(f"Error saving memory state: {e}")

        print("Goodbye from Nova!")
        sys.exit(0)

    def calculate_composite_score(self, context):
        """
        Calculate a composite score based on system metrics.
        """
        cpu_weight = 0.4
        memory_weight = 0.3
        gpu_weight = 0.3

        cpu_usage = context.get("cpu_usage", 0)
        memory_usage = context.get("memory_usage", 0)
        gpu_usage = context.get("gpu_usage", 0)

        return (
            cpu_usage * cpu_weight +
            memory_usage * memory_weight +
            gpu_usage * gpu_weight
        )

    async def monitor_events(self):
        print("Monitoring events...")
        try:
            while self.running:
                context = self.registry.query_all_engines()

                if not context:
                    print("No context returned from engines. Check engine configuration.")
                    await asyncio.sleep(1)
                    continue

                if "nova_cpu_usage" in context and context["nova_cpu_usage"] > 10:
                    print(f"Event: Nova's CPU usage is high ({context['nova_cpu_usage']}%)!")
                    await self.handle_event("Nova High CPU Usage", context)

                if "nova_memory_usage" in context and context["nova_memory_usage"] > 10:
                    print(f"Event: Nova's memory usage is high ({context['nova_memory_usage']}%)!")
                    await self.handle_event("Nova High Memory Usage", context)

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Event monitoring task was cancelled.")
            raise

    async def monitor_system_stats(self):
        print("Monitoring system stats...")
        try:
            while self.running:
                context = self.registry.query_all_engines()
                self.manager.store_context(context)

                if context.get("cpu_usage", 0) > 10:
                    print("Event: High CPU Usage Detected!")
                    await self.handle_event("High CPU Usage", context)

                trend = self.manager.detect_trends()
                if trend:
                    print(f"Trend Detected: {trend}")

                rule = self.manager.generate_dynamic_rules()
                if rule:
                    print(f"Dynamic Optimization Triggered: {rule}")

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("System stats monitoring task was cancelled.")
            raise

    async def fetch_api_data(self):
        print("Fetching API data...")
        try:
            while self.running:
                api_data = {"sx_usdc_price": random.uniform(0.95, 1.05)}
                print(f"Fetched API Data: {api_data}")

                if api_data["sx_usdc_price"] > 1.03:
                    print("Event: $SX/$USDC price spike detected!")
                    await self.handle_event("Price Spike", api_data)

                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("API data fetch task was cancelled.")
            raise

    async def handle_event(self, event_type, context):
        """
        Handles events dynamically and generates a lifelike, two-way conversation.
        """
        print(f"Handling Event: {event_type}")
        decision = self.registry.execute_dmus(context)
        self.registry.execute_action_executors(decision)
        self.manager.store_context(context)

        composite_score = self.calculate_composite_score(context)
        if composite_score > 50:
            print(f"Critical Composite Score Detected: {composite_score:.2f}")
            decision = "Take immediate action"
        elif composite_score > 30:
            print(f"Moderate Composite Score Detected: {composite_score:.2f}")
            decision = "Monitor closely"
        else:
            decision = "No action required"

        print(f"Decision: {decision}")
        self.manager.log_event(event_type, context)

        # Proactive engagement via SentienceContextEngine
        sentience_engine = self.registry.engines.get("SentienceContextEngine")
        if sentience_engine:
            print("[Nova]: Engaging proactively based on the event context...")
            query_input = f"Event detected: {event_type}. Decision: {decision}. Composite Score: {composite_score:.2f}."
            response = sentience_engine.generate_response(query_input, context)
            print(f"[Nova]: {response}")
            
            # Start a two-way conversation for critical events
            if composite_score > 50:
                follow_up = input("[Nova]: Do you want me to take immediate action or provide options? [action/options]: ").strip().lower()
                if follow_up == "action":
                    print("[Nova]: Taking immediate action as requested...")
                    # Add logic for immediate action here
                elif follow_up == "options":
                    options_response = sentience_engine.generate_response("Provide options for handling this situation.", context)
                    print(f"[Nova]: Here are your options: {options_response}")
                else:
                    print("[Nova]: Understood. Monitoring the situation closely.")



        print(f"Decision: {decision}")
        self.manager.log_event(event_type, context)

    async def handle_user_input(self):
        """
        Handles user commands dynamically with proactive and lifelike responses.
        """
        print("Nova is ready for commands. Type 'exit' to stop.")
        while self.running:
            user_input = input("[You]: ").strip()
            
            if user_input.lower() == "exit":
                print("[Nova]: Acknowledged. Shutting down...")
                await self.graceful_shutdown()
                break
            elif user_input.lower() == "status":
                print("[Nova]: Gathering current status...")
                current_context = self.registry.query_all_engines()
                print(f"Current context: {current_context}")
                
                # Proactive engagement
                sentience_engine = self.registry.engines.get("SentienceContextEngine")
                if sentience_engine:
                    response = sentience_engine.generate_response("Provide a status update with actionable insights.", current_context)
                    print(f"[Nova]: {response}")
            elif user_input.startswith("add_engine"):
                _, engine_name, module_path = user_input.split(maxsplit=2)
                print("[Nova]: Adding engine...")
                print(f"Engine Name: {engine_name}")
                print(f"Module Path: {module_path}")
                await self.registry.load_engine(engine_name, module_path)
            elif user_input.startswith("remove_engine"):
                _, engine_name = user_input.split(maxsplit=1)
                self.registry.remove_engine(engine_name)
            else:
                # Dynamic conversation fallback
                sentience_engine = self.registry.engines.get("SentienceContextEngine")
                if sentience_engine:
                    print("[Nova]: Processing your query...")
                    response = sentience_engine.generate_response(user_input)
                    print(f"[Nova]: {response}")
                else:
                    print(f"[Nova]: Sorry, I didn't understand '{user_input}'. Try 'status' or 'exit'.")
            await asyncio.sleep(0.1)


    async def run(self):
        try:
            tasks = [
                self.monitor_events(),
                self.monitor_system_stats(),
                self.fetch_api_data(),
                self.handle_user_input()
            ]

            for sig in (signal.SIGINT, signal.SIGTERM):
                asyncio.get_event_loop().add_signal_handler(sig, lambda: asyncio.create_task( self.graceful_shutdown()))

            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("Run loop was cancelled.")
        finally:
            await self.graceful_shutdown()
