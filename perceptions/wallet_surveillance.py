from utils.blockchain_wallet import BlockchainWallet
import asyncio
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

class MarketStream:
    """Fetches crypto market data from CoinGecko API."""
    def __init__(self, queue):
        self.queue = queue
        self.api_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum,bitcoin&vs_currencies=usd&include_24hr_change=true"
        asyncio.create_task(self._monitor_market())

    async def _monitor_market(self):
        while True:
            try:
                response = requests.get(self.api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    market_event = {
                        "type": "market_data",
                        "ethereum": {
                            "price": data.get("ethereum", {}).get("usd"),
                            "change_24h": data.get("ethereum", {}).get("usd_24h_change")
                        },
                        "bitcoin": {
                            "price": data.get("bitcoin", {}).get("usd"),
                            "change_24h": data.get("bitcoin", {}).get("usd_24h_change")
                        }
                    }
                    await self.queue.enqueue(market_event)
                    logging.info(f"[MarketStream] Enqueued market data: ETH ${market_event['ethereum']['price']}")
                else:
                    logging.warning(f"[MarketStream] API Error: {response.status_code}")
            except Exception as e:
                logging.error(f"[MarketStream] Error fetching data: {e}")
            
            # Rate limit: 60 seconds
            await asyncio.sleep(60)

class WalletSurveillance:
    def __init__(self, queue):
        # Fake wallet state
        self.queue = queue
        self.balance = 1000
        self.rpc_url = "https://mainnet.base.org"
        
        # Initialize sub-modules
        self.market_stream = MarketStream(queue)
        
        asyncio.create_task(self._monitor_wallet())

    async def _monitor_wallet(self):
        private_key = os.getenv("WALLET_PRIVATE_KEY", "")
        wallet = BlockchainWallet(self.rpc_url, private_key)
        address = wallet.get_address()
        balance = wallet.get_balance()
        transaction_count = wallet.get_transaction_count()

        while True:
            wallet_data = {
                    "type": "wallet_status",
                    "address": address,
                    "balance": float(balance),
                    "transaction_count": transaction_count,
                    "gas_fee": 0.0,
                }
            await self.queue.enqueue(wallet_data)
            await asyncio.sleep(60) # Slow down wallet checks too