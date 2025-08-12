from datetime import datetime
import asyncio

class TimeCartel:
    def __init__(self, queue):
        # Emit time every 1 second
        self.queue = queue
        asyncio.create_task(self._spam_time())

    async def _spam_time(self):
        while True:
            now = datetime.now()
            time = {
                "time": now.isoformat(),
                "hour": now.hour,
                "minute": now.minute,
                "day_phase": self._get_day_phase(now.hour)
            }
            await self.queue.enqueue(time)
            await asyncio.sleep(1)

    def _get_day_phase(self, hour):
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"