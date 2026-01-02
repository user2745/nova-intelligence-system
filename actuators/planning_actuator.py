import logging
import json
import os
from .actuator_manager import Actuator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class PlanningActuator(Actuator):
    """
    Actuator for planning, strategy, and goal tracking.
    """
    def __init__(self, memory_manager=None):
        super().__init__("planning")
        self.memory_manager = memory_manager
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.4)
        self.goals_file = "long_term_goals.json"
        self._load_goals()

        self.register_tool("add_goal", self.add_goal, "Add a long-term goal")
        self.register_tool("list_goals", self.list_goals, "List all active goals")
        self.register_tool("update_goal_status", self.update_goal_status, "Update status of a goal")
        self.register_tool("generate_strategy", self.generate_strategy, "Generate a strategy for a goal")
        self.register_tool("backtrack", self.backtrack, "Analyze failure and suggest backtracking")

    def _load_goals(self):
        if os.path.exists(self.goals_file):
            try:
                with open(self.goals_file, 'r') as f:
                    self.goals = json.load(f)
            except:
                self.goals = []
        else:
            self.goals = []

    def _save_goals(self):
        with open(self.goals_file, 'w') as f:
            json.dump(self.goals, f, indent=2)

    async def add_goal(self, description: str, priority: str = "medium") -> str:
        """Add a new long-term goal."""
        goal = {
            "id": len(self.goals) + 1,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": str(logging.Formatter().converter(None)) # Timestamp
        }
        self.goals.append(goal)
        self._save_goals()
        return f"Goal added: {description} (ID: {goal['id']})"

    async def list_goals(self) -> str:
        """List all goals."""
        if not self.goals:
            return "No active goals."
        return json.dumps(self.goals, indent=2)

    async def update_goal_status(self, goal_id: int, status: str) -> str:
        """Update the status of a goal (pending, in_progress, completed, failed)."""
        for goal in self.goals:
            if goal["id"] == int(goal_id):
                goal["status"] = status
                self._save_goals()
                return f"Goal {goal_id} status updated to {status}"
        return f"Goal {goal_id} not found."

    async def generate_strategy(self, goal_description: str) -> str:
        """Generate a multi-step strategy for a goal."""
        prompt = f"Create a detailed, step-by-step strategy to achieve this goal: {goal_description}. Return a numbered list."
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    async def backtrack(self, failure_reason: str) -> str:
        """Analyze a failure and suggest an alternative path."""
        prompt = f"The current plan failed due to: {failure_reason}. Suggest an alternative strategy or backtracking step."
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
