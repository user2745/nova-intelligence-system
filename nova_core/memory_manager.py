import chromadb
import logging
import time
import uuid
from typing import List, Dict, Any, Optional

class ChromaMemoryManager:
    """
    Manages the 'Trinity' memory system using ChromaDB.
    Collections:
    - episodic_stream: Stream of consciousness (thoughts, actions)
    - financial_context: Market data, wallet states
    - system_context: System logs, anomalies
    - knowledge_graph: Research, concepts, facts
    """
    
    def __init__(self, persistence_path: str = "./nova_memory_db"):
        logging.info(f"[Memory] Initializing ChromaDB at {persistence_path}")
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # Initialize Collections
        self.episodic = self.client.get_or_create_collection(name="episodic_stream")
        self.financial = self.client.get_or_create_collection(name="financial_context")
        self.system = self.client.get_or_create_collection(name="system_context")
        self.knowledge = self.client.get_or_create_collection(name="knowledge_graph")
        
        logging.info("[Memory] Collections initialized: episodic, financial, system, knowledge")

    def _add(self, collection, text: str, metadata: Dict[str, Any]):
        """Generic add method"""
        try:
            collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[str(uuid.uuid4())]
            )
            logging.debug(f"[Memory] Added to {collection.name}: {text[:50]}...")
        except Exception as e:
            logging.error(f"[Memory] Error adding to {collection.name}: {e}")

    def add_episodic(self, text: str, type: str, domain: str, drive: str = "general"):
        """Log a thought, action, or perception to the stream of consciousness."""
        metadata = {
            "timestamp": time.time(),
            "type": type,
            "domain": domain,
            "drive_influence": drive
        }
        self._add(self.episodic, text, metadata)

    def add_financial(self, description: str, asset: str, price: float, balance: float, trend: str):
        """Store financial context."""
        metadata = {
            "timestamp": time.time(),
            "asset": asset,
            "price": price,
            "wallet_balance": balance,
            "trend": trend
        }
        self._add(self.financial, description, metadata)

    def add_system(self, description: str, resource_type: str, severity: int, process_name: str = "unknown"):
        """Store system context/anomalies."""
        metadata = {
            "timestamp": time.time(),
            "resource_type": resource_type,
            "severity": severity,
            "process_name": process_name
        }
        self._add(self.system, description, metadata)

    def add_knowledge(self, content: str, source: str, tags: List[str], sentiment: float = 0.0):
        """Store research or facts."""
        # Chroma metadata cannot be lists, store tags as comma-separated string
        metadata = {
            "timestamp": time.time(),
            "source": source,
            "tags": ",".join(tags),
            "sentiment": sentiment
        }
        self._add(self.knowledge, content, metadata)

    def query(self, collection_name: str, query_text: str, n_results: int = 3) -> List[str]:
        """Retrieve relevant context from a specific collection."""
        try:
            if collection_name == "episodic":
                coll = self.episodic
            elif collection_name == "financial":
                coll = self.financial
            elif collection_name == "system":
                coll = self.system
            elif collection_name == "knowledge":
                coll = self.knowledge
            else:
                return []

            results = coll.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Flatten results
            return results['documents'][0] if results['documents'] else []
            
        except Exception as e:
            logging.error(f"[Memory] Error querying {collection_name}: {e}")
            return []
