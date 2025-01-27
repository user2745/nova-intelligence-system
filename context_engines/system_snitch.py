import asyncio
import os
import psutil
import subprocess

class SystemSnitch:
    def __init__(self, ucp):
        # Emit system stats every 2 seconds
        self.ucp = ucp
        asyncio.create_task(self._snitch_loop())

    async def _snitch_loop(self):
        process = psutil.Process(os.getpid())
        while True:
            self.ucp.emit_context({
            "system": {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "my_cpu_usage": process.cpu_percent(interval=1),
                "my_memory_usage": process.memory_percent(),
                }
            })
            await asyncio.sleep(2)

