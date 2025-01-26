# context_cartels.py
import psutil
from datetime import datetime
from rx import operators as ops
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class TimeCartel:
    def __init__(self, ucp):
        # Emit time every 1 second
        self.ucp = ucp
        asyncio.create_task(self._spam_time())

    async def _spam_time(self):
        while True:
            self.ucp.emit_context({
                "type": "time",
                "value": datetime.now().isoformat()
            })
            await asyncio.sleep(1)

class SystemSnitch:
    def __init__(self, ucp):
        # Emit system stats every 2 seconds
        self.ucp = ucp
        asyncio.create_task(self._snitch_loop())

    async def _snitch_loop(self):
        while True:
            self.ucp.emit_context({
                "type": "system",
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent
            })
            await asyncio.sleep(2)

class WalletSurveillance:
    def __init__(self, ucp):
        # Fake wallet state
        self.ucp = ucp
        self.balance = 1000
        asyncio.create_task(self._monitor_wallet())

    async def _monitor_wallet(self):
        while True:
            self.ucp.emit_context({
                "type": "wallet",
                "balance": self.balance,
                "address": "0xNova"
            })
            await asyncio.sleep(5)