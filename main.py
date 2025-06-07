# main.py
import asyncio
from ucp_pubsub import UCPPubSub
from context_engines.time_cartel import TimeCartel
from context_engines.system_snitch import SystemSnitch
from context_engines.wallet_surveillance import WalletSurveillance
from context_engines.portfolio_manager import CryptoPortfolioManager
from execution.ping_pong import PingPong
from nova_core.nova_brain_v3 import NovaBrainV3

async def main():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ucp = UCPPubSub()
            nova = NovaBrainV3(ucp)
            
            # Test context engine
            PingPong(nova.ucp)

            print("🌌 Nova is booting...")
            await asyncio.sleep(5)  # Let systems initialize

            nova.ucp.emit_context({
                "status": "live",
                "system": {
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "disk_usage": 0.0,
                    "my_cpu_usage": 0.0,
                    "my_memory_usage": 0.0
                },
                "wallet": {
                    "balance": 0.0,
                    "address": "",
                    "transaction_count": 0,
                    "gas_fee": 0.0
                },
                })
            nova.ucp.emit_state({
                        "initialized": True,
                        "mood": "neutral",
                        "last_action": "idle",
                        "task_queue": [],
                    })
            nova.ucp.emit_intent({
                    "intent": "BootUp",
                    "parameters": {
                        "user": "Nova",
                        "location": "Earth",
                    },
                })

            print("🌌 Nova is ready to serve.")
            while True:
                try:
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Recovered from error: {e}")
                    continue
                    
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Restarting due to error: {e}")
            await asyncio.sleep(5 * attempt)

if __name__ == "__main__":
    asyncio.run(main())