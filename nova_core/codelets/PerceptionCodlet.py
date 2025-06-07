# perceptual_codelet.py
import asyncio, logging
class PerceptionlCodelet:
    UPDATE_HZ = 1.0          # override per subclass

    def __init__(self, ucp):
        self.ucp = ucp
        asyncio.create_task(self._loop())

    async def _loop(self):
        dt = 1.0 / self.UPDATE_HZ
        while True:
            try:
                payload = await self.perceive()
                if payload:                      # skip empties
                    self.ucp.emit_context(payload)
            except Exception as e:
                logging.exception(f"{self.__class__.__name__} error: {e}")
            await asyncio.sleep(dt)

    async def perceive(self):
        raise NotImplementedError
