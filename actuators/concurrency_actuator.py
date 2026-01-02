import logging
import asyncio
import json
from .actuator_manager import Actuator

class ConcurrencyActuator(Actuator):
    """
    Actuator for parallel execution, batch processing, and pipelines.
    """
    def __init__(self, actuator_manager=None, memory_manager=None):
        super().__init__("concurrency")
        self.actuator_manager = actuator_manager
        self.memory_manager = memory_manager
        self.background_tasks = {}

        self.register_tool("parallel_research", self.parallel_research, "Run multiple search queries in parallel")
        self.register_tool("batch_process", self.batch_process, "Run a tool multiple times with different args")
        self.register_tool("run_pipeline", self.run_pipeline, "Execute a sequence of tools where output of one is input to next")
        self.register_tool("async_execute", self.async_execute, "Run a tool in the background")
        self.register_tool("check_async_status", self.check_async_status, "Check status of a background task")

    async def parallel_research(self, queries: list) -> str:
        """
        Execute multiple research queries in parallel.
        """
        if not self.actuator_manager:
            return "Error: ActuatorManager not linked."
        
        research_actuator = self.actuator_manager.actuators.get("research")
        if not research_actuator:
            return "Error: Research actuator not found."

        logging.info(f"[Concurrency] Starting parallel research for {len(queries)} queries")
        
        async def run_query(q):
            # We call the tool method directly. 
            # Note: We need to find the method bound to the tool name.
            # The actuator stores tools in self.tools = {name: func}
            func = research_actuator.tools.get("quick_search")
            if func:
                return await func(q)
            return f"Error: quick_search not found"

        results = await asyncio.gather(*[run_query(q) for q in queries])
        
        combined_results = {}
        for q, r in zip(queries, results):
            combined_results[q] = r
            
        return json.dumps(combined_results, indent=2)

    async def batch_process(self, tool_name: str, args_list: list) -> str:
        """
        Run a specific tool multiple times with a list of arguments.
        args_list should be a list of dictionaries (kwargs) or single values.
        """
        if not self.actuator_manager:
            return "Error: ActuatorManager not linked."

        # Parse tool name "actuator.tool"
        if "." not in tool_name:
            return "Error: Tool name must be 'actuator.tool'"
        
        actuator_name, method_name = tool_name.split(".", 1)
        actuator = self.actuator_manager.actuators.get(actuator_name)
        
        if not actuator:
            return f"Error: Actuator {actuator_name} not found."
        
        func = actuator.tools.get(method_name)
        if not func:
            return f"Error: Tool {method_name} not found in {actuator_name}."

        logging.info(f"[Concurrency] Batch processing {len(args_list)} items for {tool_name}")

        async def run_item(arg):
            try:
                if isinstance(arg, dict):
                    return await func(**arg)
                else:
                    return await func(arg)
            except Exception as e:
                return f"Error: {e}"

        results = await asyncio.gather(*[run_item(arg) for arg in args_list])
        return json.dumps(results, indent=2)

    async def run_pipeline(self, steps: list) -> str:
        """
        Execute a pipeline of tools.
        steps: [{"tool": "actuator.tool", "arg_map": {"param_name": "prev_output"}}]
        This is a simplified pipeline where the output of step N is passed to step N+1.
        """
        # Simplified implementation: Just run sequentially and pass output as first arg if not specified
        current_input = None
        results = []

        for i, step in enumerate(steps):
            tool_name = step.get("tool")
            # Logic to map previous output to current input would go here.
            # For this MVP, we'll just say we run them in order.
            
            # ... (Implementation of full pipeline logic is complex, 
            # let's simplify to just sequential execution of a list of commands)
            pass
        
        return "Pipeline execution not fully implemented in this MVP. Use batch_process for now."

    async def async_execute(self, tool_name: str, args: dict) -> str:
        """
        Start a tool execution in the background.
        """
        import uuid
        task_id = str(uuid.uuid4())[:8]
        
        async def task_wrapper():
            try:
                # Resolve tool
                if "." not in tool_name:
                    self.background_tasks[task_id] = {"status": "failed", "result": "Invalid tool name"}
                    return

                actuator_name, method_name = tool_name.split(".", 1)
                actuator = self.actuator_manager.actuators.get(actuator_name)
                if not actuator:
                    self.background_tasks[task_id] = {"status": "failed", "result": "Actuator not found"}
                    return
                
                func = actuator.tools.get(method_name)
                if not func:
                    self.background_tasks[task_id] = {"status": "failed", "result": "Tool not found"}
                    return

                result = await func(**args)
                self.background_tasks[task_id] = {"status": "completed", "result": result}
            except Exception as e:
                self.background_tasks[task_id] = {"status": "failed", "result": str(e)}

        self.background_tasks[task_id] = {"status": "running", "result": None}
        asyncio.create_task(task_wrapper())
        
        return f"Task started with ID: {task_id}. Use check_async_status to view results."

    async def check_async_status(self, task_id: str) -> str:
        """Check the status of a background task."""
        task = self.background_tasks.get(task_id)
        if not task:
            return "Task not found."
        return json.dumps(task, indent=2)
