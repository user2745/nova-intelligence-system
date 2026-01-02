import asyncio
import logging
import sys
import os
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_module import CoreModule

async def run_test():
    print("Initializing Core...")
    core = CoreModule()
    
    # Initialize but don't run the infinite loop in start()
    # We manually do what start() does but without the while True
    await core.initialize()
    
    # Start cognitive cycle in background
    asyncio.create_task(core.brain.cognitive_cycle())
    
    print("Waiting for system to settle (10s)...")
    await asyncio.sleep(10)
    
    # Command 1: Check system status
    cmd1 = "Check the system status and list all active network connections"
    print(f"Injecting Command 1: {cmd1}")
    await core.real_time_queue.enqueue({
        "type": "cli_input",
        "payload": {"message": cmd1},
        "source": "user",
        "timestamp": time.time()
    })
    
    print("Waiting for Command 1 execution (30s)...")
    await asyncio.sleep(30)
    
    # Command 2: Create python script
    cmd2 = "Create a python script called monitor_cpu.py that logs CPU usage to a file every 5 seconds"
    print(f"Injecting Command 2: {cmd2}")
    await core.real_time_queue.enqueue({
        "type": "cli_input",
        "payload": {"message": cmd2},
        "source": "user",
        "timestamp": time.time()
    })
    
    print("Waiting for Command 2 execution (30s)...")
    await asyncio.sleep(30)
    
    print("Test Complete. Shutting down.")
    core.brain.running = False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_test())
