import asyncio
from core.nova_core import NovaCore

async def main():
    core = NovaCore()
    core.initialize()

    try:
        await core.run()
    except asyncio.CancelledError:
        await core.graceful_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
