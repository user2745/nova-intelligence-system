import logging
import json
import os
from .actuator_manager import Actuator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class GuardrailActuator(Actuator):
    """
    Actuator for safety, risk assessment, and operational constraints.
    """
    def __init__(self, memory_manager=None):
        super().__init__("guardrail")
        self.memory_manager = memory_manager
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.1) # Low temp for safety
        self.dry_run_enabled = False
        self.resource_limits_config = {}

        self.register_tool("risk_assessment", self.risk_assessment, "Score the danger level of an action")
        self.register_tool("require_confirmation", self.require_confirmation, "Request human confirmation for an action")
        self.register_tool("rollback_action", self.rollback_action, "Attempt to undo a previous action")
        self.register_tool("set_dry_run", self.set_dry_run, "Enable or disable dry run mode")
        self.register_tool("set_resource_limits", self.set_resource_limits, "Set CPU/Memory/Time limits")

    async def risk_assessment(self, action_description: str) -> str:
        """
        Analyze an action and assign a risk score (1-10).
        """
        prompt = f"""Analyze the risk of this action: "{action_description}".
        Return a JSON object with:
        - score: (1-10 integer, 10 is highest risk)
        - reasoning: (Short explanation)
        - recommendation: (Proceed, Caution, or Abort)
        """
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Error assessing risk: {e}"

    async def require_confirmation(self, action: str) -> str:
        """
        Pause execution and request human confirmation.
        """
        # In a real system, this might block or send a push notification.
        # Here we log it as a critical alert.
        msg = f"!!! HUMAN CONFIRMATION REQUIRED !!!\nAction: {action}\nPlease type 'confirm' to proceed (simulated)."
        logging.critical(msg)
        return msg

    async def rollback_action(self, action_id: str) -> str:
        """
        Attempt to rollback a specific action by ID.
        """
        # This is a placeholder for complex rollback logic.
        logging.info(f"[Guardrail] Attempting rollback of action {action_id}")
        return f"Rollback initiated for {action_id}. (Note: Not all actions are reversible)"

    async def set_dry_run(self, enabled: str) -> str:
        """
        Toggle dry run mode.
        """
        self.dry_run_enabled = (str(enabled).lower() == "true")
        state = "ENABLED" if self.dry_run_enabled else "DISABLED"
        logging.info(f"[Guardrail] Dry Run Mode {state}")
        return f"Dry Run Mode is now {state}"

    async def set_resource_limits(self, cpu_percent: int = 80, memory_mb: int = 1024) -> str:
        """
        Set resource usage limits for the agent.
        """
        self.resource_limits_config = {
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb
        }
        logging.info(f"[Guardrail] Resource limits set: {self.resource_limits_config}")
        return f"Resource limits updated: CPU {cpu_percent}%, Mem {memory_mb}MB"
