import logging
import os
from .actuator_manager import Actuator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class CodingActuator(Actuator):
    """
    Actuator for code generation, debugging, and optimization.
    """
    def __init__(self, memory_manager=None):
        super().__init__("coding")
        self.memory_manager = memory_manager
        self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.1"), temperature=0.2) # Low temp for coding

        self.register_tool("generate_script", self.generate_script, "Generate a script from a description")
        self.register_tool("debug_code", self.debug_code, "Debug code given an error message")
        self.register_tool("optimize_code", self.optimize_code, "Optimize code for performance")
        self.register_tool("test_generation", self.test_generation, "Generate unit tests for code")

    async def generate_script(self, task_description: str, language: str = "python") -> str:
        """Generate a script based on a natural language description."""
        try:
            prompt = f"Write a {language} script to: {task_description}. Return ONLY the code, no markdown, no explanation."
            response = self.llm.invoke([HumanMessage(content=prompt)])
            code = response.content
            logging.info(f"[CodingActuator] Generated script for: {task_description}")
            return code
        except Exception as e:
            logging.error(f"[CodingActuator] Error generating script: {e}")
            return f"Error: {e}"

    async def debug_code(self, code: str, error: str) -> str:
        """Attempt to fix code based on an error message."""
        try:
            prompt = f"Fix this code:\n\n{code}\n\nError:\n{error}\n\nReturn ONLY the fixed code."
            response = self.llm.invoke([HumanMessage(content=prompt)])
            fixed_code = response.content
            logging.info(f"[CodingActuator] Debugged code")
            return fixed_code
        except Exception as e:
            logging.error(f"[CodingActuator] Error debugging code: {e}")
            return f"Error: {e}"

    async def optimize_code(self, code: str) -> str:
        """Optimize the given code for performance and readability."""
        try:
            prompt = f"Optimize this code for performance and readability:\n\n{code}\n\nReturn ONLY the optimized code."
            response = self.llm.invoke([HumanMessage(content=prompt)])
            optimized_code = response.content
            logging.info(f"[CodingActuator] Optimized code")
            return optimized_code
        except Exception as e:
            logging.error(f"[CodingActuator] Error optimizing code: {e}")
            return f"Error: {e}"

    async def test_generation(self, code: str) -> str:
        """Generate unit tests for the given code."""
        try:
            prompt = f"Write unit tests (using pytest/unittest) for this code:\n\n{code}\n\nReturn ONLY the test code."
            response = self.llm.invoke([HumanMessage(content=prompt)])
            tests = response.content
            logging.info(f"[CodingActuator] Generated tests")
            return tests
        except Exception as e:
            logging.error(f"[CodingActuator] Error generating tests: {e}")
            return f"Error: {e}"
