
class HealthManager:
    def __init__(self, bot):
        self.bot = bot

    async def start(self):
        # Start the health check loop
        asyncio.create_task(self._health_check_loop())
    async def _health_check_loop(self):
        @On(bot, "health")
        self.ucp.emit_context({
            "my_health": {
                "health": bot.health,
                "food": bot.food,
            }
        })