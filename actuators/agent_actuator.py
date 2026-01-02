import logging
import os
from .actuator_manager import Actuator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class AgentActuator(Actuator):
    """
    Actuator for spawning sub-agents and specialized tasks.
    """
    def __init__(self, memory_manager=None):
        super().__init__("agent")
        self.memory_manager = memory_manager
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.3)

        self.register_tool("spawn_subagent", self.spawn_subagent, "Delegate a task to a sub-agent")
        self.register_tool("consult_expert", self.consult_expert, "Ask a specialized expert agent")

    async def spawn_subagent(self, task: str, constraints: str = "") -> str:
        """
        Spawn a transient sub-agent to perform a specific task.
        In reality, this runs a focused LLM chain.
        """
        logging.info(f"[AgentActuator] Spawning sub-agent for: {task}")
        system_prompt = f"""You are a specialized sub-agent tasked with: {task}.
        Constraints: {constraints}.
        Solve the problem and return the result concisely."""
        
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Execute your task.")
        ])
        return f"Sub-agent Report:\n{response.content}"

    async def consult_expert(self, role: str, question: str) -> str:
        """
        Consult a specialized expert (e.g., 'Security Expert', 'Python Guru').
        """
        logging.info(f"[AgentActuator] Consulting {role}")
        system_prompt = f"You are a world-class {role}. Answer the user's question with high expertise."
        
        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ])
        return f"{role} Advice:\n{response.content}"
