# main.py
import json
from ucp_pubsub import UCPPubSub
from blockchain_merc import EVMMercenaries
from context_cartels import TimeCartel, SystemSnitch, WalletSurveillance
from llm_mafia import DeepThinkMafia
import asyncio

async def main():
    # Initialize the streets
    ucp = UCPPubSub()

    # ===== ADD DEBUG SUBSCRIBERS =====
    # Log all context updates
    ucp.command_stream.subscribe(
        lambda ctx: print(f"📥 [COMMAND] {ctx}")
    )

    ucp.transaction_stream.subscribe(
        lambda tx: print(f"⛓ [TX] {tx}")
    )

    ucp.context_stream.subscribe(
        lambda ctx: print(f"🌍 [CONTEXT] {json.dumps(ctx, indent=2)}")
    )
    # Log all responses
    ucp.response_stream.subscribe(
        lambda resp: print(f"📢 [RESPONSE] {resp}")
    )
    # ================================

    ucp.emit_context({"status": "ready"}) # Notify the world


    # Context engines
    EVMMercenaries(ucp)
    TimeCartel(ucp)
    SystemSnitch(ucp)
    WalletSurveillance(ucp)

    # AI Decision-Maker
    DeepThinkMafia(ucp)



    # Simulate user command
    print("\n🔥 SENDING TEST COMMAND...")
    ucp.emit_command({
        "action": "user_request",
        "user": "0xHacker",
        "request": "send 100 ETH to Vitalik"
    })

    # Keep alive to hear context spam
    while True:
        await asyncio.sleep(1)

asyncio.run(main())