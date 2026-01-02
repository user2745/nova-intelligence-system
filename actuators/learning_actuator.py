import logging
import json
import os
from .actuator_manager import Actuator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class LearningActuator(Actuator):
    """
    Actuator for learning loops, failure analysis, and optimization.
    """
    def __init__(self, memory_manager=None):
        super().__init__("learning")
        self.memory_manager = memory_manager
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.3)
        self.history_file = "action_history.json"
        self._load_history()

        self.register_tool("log_outcome", self.log_outcome, "Log the outcome of an action")
        self.register_tool("analyze_failures", self.analyze_failures, "Analyze recent failures")
        self.register_tool("suggest_optimization", self.suggest_optimization, "Suggest tool usage optimizations")

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

    def _save_history(self):
        # Keep only last 100 entries to avoid bloat
        if len(self.history) > 100:
            self.history = self.history[-100:]
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    async def log_outcome(self, tool_name: str, success: bool, notes: str = "") -> str:
        """Log the success or failure of a tool usage."""
        entry = {
            "tool": tool_name,
            "success": success,
            "notes": notes,
            "timestamp": str(logging.Formatter().converter(None))
        }
        self.history.append(entry)
        self._save_history()
        return "Outcome logged."

    async def analyze_failures(self) -> str:
        """Analyze recent failures to find patterns."""
        failures = [h for h in self.history if not h["success"]]
        if not failures:
            return "No recent failures found."
        
        prompt = f"Analyze these recent failures and suggest a fix:\n{json.dumps(failures, indent=2)}"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    async def suggest_optimization(self) -> str:
        """Suggest improvements based on usage history."""
        prompt = f"Based on this usage history, suggest optimizations:\n{json.dumps(self.history, indent=2)}"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
