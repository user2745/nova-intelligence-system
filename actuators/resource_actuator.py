import logging
import json
import asyncio
from .actuator_manager import Actuator

class ResourceActuator(Actuator):
    """
    Actuator for resource management, task queues, and scheduling.
    """
    def __init__(self, memory_manager=None):
        super().__init__("resource")
        self.memory_manager = memory_manager
        self.task_queue = [] # List of {"id": str, "task": str, "priority": int, "status": str}
        self.next_id = 1

        self.register_tool("add_task", self.add_task, "Add a task to the queue")
        self.register_tool("prioritize_task", self.prioritize_task, "Change task priority")
        self.register_tool("list_tasks", self.list_tasks, "List all tasks in queue")
        self.register_tool("get_next_task", self.get_next_task, "Get the highest priority pending task")
        self.register_tool("mark_task_complete", self.mark_task_complete, "Mark a task as completed")

    async def add_task(self, description: str, priority: int = 1) -> str:
        """Add a task to the queue. Higher priority number = higher importance."""
        task = {
            "id": self.next_id,
            "description": description,
            "priority": int(priority),
            "status": "pending",
            "created_at": str(asyncio.get_event_loop().time())
        }
        self.task_queue.append(task)
        self.next_id += 1
        # Sort queue by priority (descending)
        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        return f"Task added: ID {task['id']}"

    async def prioritize_task(self, task_id: int, new_priority: int) -> str:
        """Update the priority of a task."""
        for task in self.task_queue:
            if task["id"] == int(task_id):
                task["priority"] = int(new_priority)
                self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
                return f"Task {task_id} priority updated to {new_priority}"
        return f"Task {task_id} not found"

    async def list_tasks(self, status_filter: str = None) -> str:
        """List tasks, optionally filtered by status (pending, completed)."""
        if status_filter:
            filtered = [t for t in self.task_queue if t["status"] == status_filter]
            return json.dumps(filtered, indent=2)
        return json.dumps(self.task_queue, indent=2)

    async def get_next_task(self) -> str:
        """Get the highest priority pending task."""
        pending = [t for t in self.task_queue if t["status"] == "pending"]
        if not pending:
            return "No pending tasks."
        # Since list is sorted, first pending is highest priority
        return json.dumps(pending[0], indent=2)

    async def mark_task_complete(self, task_id: int) -> str:
        """Mark a task as completed."""
        for task in self.task_queue:
            if task["id"] == int(task_id):
                task["status"] = "completed"
                return f"Task {task_id} marked as completed."
        return f"Task {task_id} not found"
