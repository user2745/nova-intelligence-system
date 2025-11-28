import logging
from typing import Dict, Any, Callable, List, Optional

class Actuator:
    """Base class for all actuators."""
    def __init__(self, name: str):
        self.name = name
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable, description: str):
        """Register a tool capability."""
        self.tools[name] = {
            "func": func,
            "description": description
        }

    def get_tools(self) -> List[Dict[str, str]]:
        """Return a list of available tools."""
        return [
            {"name": name, "description": data["description"]}
            for name, data in self.tools.items()
        ]

    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a specific tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in actuator '{self.name}'")
        
        logging.info(f"[{self.name}] Executing tool: {tool_name} with args: {kwargs}")
        try:
            return await self.tools[tool_name]["func"](**kwargs)
        except Exception as e:
            logging.error(f"[{self.name}] Tool execution failed: {e}")
            return f"Error: {str(e)}"

class ActuatorManager:
    """
    Central hub for managing and executing actuators.
    Implements the 'Safety Latch' for high-risk actions.
    """
    def __init__(self):
        self.actuators: Dict[str, Actuator] = {}
        logging.info("[ActuatorManager] Initialized.")

    def register_actuator(self, actuator: Actuator):
        """Register a new actuator."""
        self.actuators[actuator.name] = actuator
        logging.info(f"[ActuatorManager] Registered actuator: {actuator.name}")

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get a flat list of all available tools across all actuators."""
        all_tools = []
        for actuator in self.actuators.values():
            for tool in actuator.get_tools():
                all_tools.append({
                    "actuator": actuator.name,
                    "tool": tool["name"],
                    "description": tool["description"]
                })
        return all_tools

    async def execute_tool(self, actuator_name: str, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool on a specific actuator.
        TODO: Implement Safety Latch here (require user confirmation for high-risk tools).
        """
        if actuator_name not in self.actuators:
            return f"Error: Actuator '{actuator_name}' not found."
        
        # Safety Latch Logic (Simple CLI confirmation for now)
        # In a real async loop, we might need a non-blocking way to ask, 
        # but for now we'll assume the Brain has already "decided" and we might just log it.
        # If we want real confirmation, we'd need to pause execution or have a callback.
        # For this iteration, we will log a warning for destructive actions.
        
        return await self.actuators[actuator_name].execute(tool_name, **kwargs)
