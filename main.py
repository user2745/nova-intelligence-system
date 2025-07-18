# main.py
import asyncio
from ucp_pubsub import UCPPubSub
from nova_body.nova_body import NovaBody
from nova_core.nova_brain_v3 import NovaBrainV3



async def main():
    max_retries = 3
    for attempt in range(max_retries):
        try:

            ucp = UCPPubSub()
            nova = NovaBrainV3(ucp)
            novaBody = NovaBody()
            novaBody.start()


            print("🌌 Nova is booting...")
            await asyncio.sleep(5)  # Let systems initialize

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