from real_time_queue import RealTimeQueue
import uuid
import asyncio
import logging
import json

class CLIBody:
    """Perception component reading CLI input as events."""
    def __init__(self, bus: RealTimeQueue):
        self.bus = bus

    async def start(self):
        logging.info("[CLIBody] Ready for input. Type messages to emit perception events.")
        while True:
            # Read user input without blocking event loop
            message = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            event = {
                "id": str(uuid.uuid4()),
                "type": "cli_input",
                "payload": {"message": message}
            }
            await self.bus.enqueue(event)