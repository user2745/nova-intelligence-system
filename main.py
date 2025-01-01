import asyncio
from core.context.immutable_context import ImmutableContext
from core.nova_core import NovaCore

async def main():
    context = ImmutableContext()
    core = NovaCore(context)
    core.initialize()

    try:
        await core.run()
    except asyncio.CancelledError:
        await core.graceful_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
