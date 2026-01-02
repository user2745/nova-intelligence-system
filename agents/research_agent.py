import asyncio
import logging
# from duckduckgo_search import DDGS # Deprecated
from ddgs import DDGS

class WebCrawler:
    """
    The Research Agent.
    Allows Nova to search the web for information to satisfy the 'Strategic Intelligence' drive.
    """
    def __init__(self, queue):
        self.queue = queue
        self.ddgs = DDGS()
        logging.info("[WebCrawler] Initialized.")

    async def search(self, query: str, max_results: int = 3):
        """
        Perform a web search and enqueue the results.
        This is usually triggered by a Brain command, not a loop.
        """
        logging.info(f"[WebCrawler] Searching for: {query}")
        try:
            results = self.ddgs.text(query, max_results=max_results)
            if results:
                research_event = {
                    "type": "research_result",
                    "query": query,
                    "results": results
                }
                await self.queue.enqueue(research_event)
                logging.info(f"[WebCrawler] Found {len(results)} results for '{query}'")
            else:
                logging.warning(f"[WebCrawler] No results found for '{query}'")
                
        except Exception as e:
            logging.error(f"[WebCrawler] Search error: {e}")