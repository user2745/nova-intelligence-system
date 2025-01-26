# context_cartels.py
import psutil
from datetime import datetime
from rx import operators as ops
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import os
import psutil
import subprocess
from engines.modules.blockchain_wallet import BlockchainWallet

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


class WalletSurveillance:
    def __init__(self, ucp):
        # Fake wallet state
        self.ucp = ucp
        self.balance = 1000
        self.rpc_url = "https://mainnet.base.org"
        asyncio.create_task(self._monitor_wallet())

    async def _monitor_wallet(self):
        private_key = os.environ.get("WALLET_PRIVATE_KEY", "")
        wallet = BlockchainWallet(self.rpc_url, private_key)
        address = wallet.get_address()
        balance = wallet.get_balance()
        transaction_count = wallet.get_transaction_count()

        while True:
            self.ucp.emit_context({
                "wallet": {
                    "address": address,
                    "balance": str(balance),
                    "transaction_count": transaction_count,
                }
            })
            await asyncio.sleep(5)