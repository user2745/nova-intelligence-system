# Working memory is a chroma database with supplementary in-memory TTL cache.
import logging
import os
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma


class WorkingMemory(object):


    def __init__(self) -> None:
            embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_MODEL", "llama3.1"))
            self.vector_store = Chroma(
                collection_name="example_collection",
                embedding_function=embeddings,
            )

    def _preprocessing_payload(self, payload):
        """
        Preprocess the payload for storage.
        Convert dict to Document object.
        """
        if isinstance(payload, dict):
            return Document(
                page_content=str(payload),
                metadata=payload
            )
        return Document(
            page_content=str(payload),
            metadata={"content": payload}
        )

    def write(self, payload):
        """
        Write to the working memory.
        """
        try:
            logging.debug(f"Writing payload to working memory: {payload}")
            # Store the payload in the vector store
            # Convert dict to Document object
            # Flatten metadata to avoid ChromaDB errors with nested dicts
            safe_metadata = {}
            if isinstance(payload, dict):
                for k, v in payload.items():
                    if isinstance(v, (str, int, float, bool)):
                        safe_metadata[k] = v
                    else:
                        safe_metadata[k] = str(v)
            else:
                safe_metadata = {"content": str(payload)}

            doc = Document(
                page_content=str(payload),
                metadata=safe_metadata
            )
            self.vector_store.add_documents([doc])
            logging.debug(f"Payload written to working memory: {payload}")
        except Exception as e:
            logging.error(f"Failed to write to working memory: {e}")

    def read(self, payload):
        """
        Read from the working memory.
        """
        try:
            # Retrieve the payload from the vector store
            results = self.vector_store.query(query_texts=[payload])
            logging.info(f"Payload read from working memory: {results}")
            return results
        except Exception as e:
            logging.error(f"Failed to read from working memory: {e}")
            return None

    