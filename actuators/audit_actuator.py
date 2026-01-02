import logging
import json
import os
from datetime import datetime
from .actuator_manager import Actuator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class AuditActuator(Actuator):
    """
    Actuator for audit trails, provenance, and compliance logging.
    """
    def __init__(self, memory_manager=None):
        super().__init__("audit")
        self.memory_manager = memory_manager
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.2)
        self.compliance_log_file = "compliance_audit.log"

        self.register_tool("action_provenance", self.action_provenance, "Explain why an action was taken")
        self.register_tool("decision_replay", self.decision_replay, "Reconstruct context for a past decision")
        self.register_tool("compliance_logging", self.compliance_logging, "Log an event to the immutable compliance record")
        self.register_tool("blame_assignment", self.blame_assignment, "Analyze a failure to determine the root cause")

    async def action_provenance(self, action_id: str) -> str:
        """
        Retrieve the chain of thought and drive state that led to an action.
        """
        # In a full implementation, this would query the vector DB or history.
        # For now, we simulate the retrieval.
        return f"Provenance for {action_id}: Triggered by [Security Drive] due to [Suspicious Network Activity] detected at [Timestamp]."

    async def decision_replay(self, decision_id: str) -> str:
        """
        Simulate a replay of the decision-making process.
        """
        return f"Replaying Decision {decision_id}: Context loaded. State restored. Agent logic re-evaluated. Outcome: Consistent."

    async def compliance_logging(self, event_type: str, details: str) -> str:
        """
        Log a regulatory or compliance-critical event.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
            "signature": "NOVA-CORE-SIGNED" # Simulated signature
        }
        
        with open(self.compliance_log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        logging.info(f"[Audit] Compliance event logged: {event_type}")
        return "Event logged to compliance record."

    async def blame_assignment(self, failure_context: str) -> str:
        """
        Analyze a failure to assign 'blame' (root cause analysis).
        """
        prompt = f"""Analyze this failure context and determine the root cause (Component, External, or Logic Error):
        Context: {failure_context}
        Return a concise Root Cause Analysis."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Error analyzing blame: {e}"
