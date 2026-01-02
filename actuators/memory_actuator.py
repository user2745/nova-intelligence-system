import logging
import json
from .actuator_manager import Actuator

class MemoryActuator(Actuator):
    """
    Actuator for interacting with the system's long-term memory (ChromaDB).
    Allows the agent to recall information and store new knowledge.
    """
    def __init__(self, memory_manager=None):
        super().__init__("memory")
        self.memory_manager = memory_manager

        self.register_tool("recall", self.recall, "Search long-term memory for context")
        self.register_tool("memorize", self.memorize, "Store new knowledge in long-term memory")

    async def recall(self, query: str, domain: str = "knowledge") -> str:
        """
        Search memory for a specific query.
        Domain options: 'knowledge', 'episodic', 'system', 'financial'.
        """
        if not self.memory_manager:
            return "Error: Memory manager not connected."
        
        try:
            results = self.memory_manager.query(collection_name=domain, query_text=query, n_results=3)
            if not results or not results[0]:
                return f"No relevant memories found in {domain} for '{query}'."
            
            # Chroma returns list of lists, flatten it
            flat_results = [item for sublist in results for item in sublist]
            return f"Memory Recall ({domain}):\n" + "\n---\n".join(flat_results)
        except Exception as e:
            logging.error(f"[MemoryActuator] Error recalling memory: {e}")
            return f"Error recalling memory: {e}"

    async def memorize(self, content: str, tags: str = "general") -> str:
        """
        Store a new piece of knowledge.
        """
        if not self.memory_manager:
            return "Error: Memory manager not connected."
        
        try:
            tag_list = [t.strip() for t in tags.split(",")]
            self.memory_manager.add_knowledge(content=content, source="agent_reflection", tags=tag_list)
            return "Knowledge stored successfully."
        except Exception as e:
            logging.error(f"[MemoryActuator] Error storing memory: {e}")
            return f"Error storing memory: {e}"
