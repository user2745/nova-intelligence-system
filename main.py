# main.py
import asyncio
from ucp_pubsub import UCPPubSub
from context_engines.time_cartel import TimeCartel
from context_engines.system_snitch import SystemSnitch
from context_engines.wallet_surveillance import WalletSurveillance
from execution.blockchain_merc import EVMMercenaries
from nova_core.nova_core import NovaCore

async def main():
    ucp = UCPPubSub()
    nova = NovaCore(ucp)
    
    # Context providers
    TimeCartel(nova.ucp)
    SystemSnitch(nova.ucp)
    WalletSurveillance(nova.ucp)
    EVMMercenaries(nova.ucp)
    
    await asyncio.sleep(1)  # Let systems initialize
    print("🌌 Nova is booting...")
    
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())