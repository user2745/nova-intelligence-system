from utils.blockchain_wallet import BlockchainWallet
import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class WalletSurveillance:
    def __init__(self, queue):
        # Fake wallet state
        self.queue = queue
        self.balance = 1000
        self.rpc_url = "https://mainnet.base.org"
        asyncio.create_task(self._monitor_wallet())

    async def _monitor_wallet(self):
        private_key = os.getenv("WALLET_PRIVATE_KEY", "")
        wallet = BlockchainWallet(self.rpc_url, private_key)
        address = wallet.get_address()
        balance = wallet.get_balance()
        transaction_count = wallet.get_transaction_count()

        while True:
            wallet = {
                    "address": address,
                    "balance": float(balance),
                    "transaction_count": transaction_count,
                    "gas_fee": 0.0,
                }
            await self.queue.enqueue(wallet)
            await asyncio.sleep(5)