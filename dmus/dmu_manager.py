# dmu_manager.py
import asyncio
from core.memory_manager import AIDMUWithMemory  # Added import

class DMUManager:
    def __init__(self, mutable_context, memory_manager):
        self.context = mutable_context
        self.llm = AIDMUWithMemory(memory_manager=memory_manager, llm_url="http://localhost:11434/api/chat", model_name="deepthink-r1")
        self.executor = None  # Will be injected from NovaCore

    async def make_decisions(self):
        """Main decision loop using deepthink-r1"""
        try:
            while True:
                context = self._format_context()
                decision = await self.llm.run(context)
                await self._execute_llm_decision(decision)
                await asyncio.sleep(5)  # Throttle decisions
        except asyncio.CancelledError:
            print("Decision loop cancelled")

    def _format_context(self):
        """Unified context formatting for LLM"""
        raw_ctx = self.context.get_current_context()
        return (
            f"System Status: CPU {raw_ctx.get('CPU_usage', '?')}%, "
            f"Memory {raw_ctx.get('memory_usage', '?')}%. "
            f"Time: {raw_ctx.get('time_of_day', {}).get('time', '?')}. "
            f"Wallet: {raw_ctx.get('wallet_status', {}).get('balance', '?')} ETH"
        )

    async def _execute_llm_decision(self, decision):
        """Parse and validate LLM output"""
        if "ACTION:" in decision:
            action = self._parse_action(decision)
            if action and self._validate_action(action):
                print(f"Executing: {action['command']}")
                await self.executor.add_task(1, action["module"], action["params"])

    def _parse_action(self, decision):
        """Simple action parser (temp implementation)"""
        try:
            cmd_part = decision.split("ACTION:")[1].strip()
            return {
                "command": cmd_part,
                "module": "blockchain_transaction_executor" if "send" in cmd_part else "generic",
                "params": {"instruction": cmd_part}
            }
        except:
            return None

    def _validate_action(self, action):
        """Basic safety checks"""
        if "send" in action["command"] and "all funds" in action["command"]:
            print("Blocking dangerous funds transfer!")
            return False
        return True