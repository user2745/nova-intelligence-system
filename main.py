# main.py
import asyncio
from ucp_pubsub import UCPPubSub
from context_engines.speech_recognition import SpeechRecognition
from nova_core.intent_processing_engine import IntentProcessingEngine
from context_engines.time_cartel import TimeCartel
from context_engines.system_snitch import SystemSnitch
from context_engines.wallet_surveillance import WalletSurveillance
from context_engines.portfolio_manager import CryptoPortfolioManager
from nova_core.ping_pong import PingPong
from nova_core.nova_core import NovaCore

async def main():
    ucp = UCPPubSub()
    nova = NovaCore(ucp)
    
    # Context providers
    TimeCartel(nova.ucp)
    SystemSnitch(nova.ucp)
    WalletSurveillance(nova.ucp)
    # SpeechRecognition(nova.ucp)

    # Context consumers
    CryptoPortfolioManager(nova.ucp)
    IntentProcessingEngine(nova.ucp)

    # Test context engine
    PingPong(nova.ucp)

    
    await asyncio.sleep(1)  # Let systems initialize
    print("🌌 Nova is booting...")
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
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())