from datetime import datetime
import asyncio

class TimeCartel:
    def __init__(self, ucp):
        # Emit time every 1 second
        self.ucp = ucp
        asyncio.create_task(self._spam_time())

    async def _spam_time(self):
        while True:
            self.ucp.emit_context({
                "time": datetime.now().isoformat()
            })
            await asyncio.sleep(1)

