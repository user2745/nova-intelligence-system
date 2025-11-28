import logging
from datetime import datetime

from .actuator_manager import Actuator
from agents.research_agent import WebCrawler
from agents.research import run_research_task

class ResearchActuator(Actuator):
    """
    Actuator for information gathering.
    Uses the WebCrawler to perform searches.
    """
    def __init__(self, web_crawler: WebCrawler, memory_manager=None):
        super().__init__("research")
        self.web_crawler = web_crawler
        self.memory_manager = memory_manager
        self.register_tool("quick_search", self.quick_search, "Perform a deep web search on a topic")
        self.register_tool(
            "deep_research",
            self.deep_research,
            "Run an LLM-powered deep research task and store the result in memory",
        )

    async def quick_search(self, query: str) -> str:
        """
        Perform a search and store an intel brief only in Chroma.
        """
        logging.info(f"[ResearchActuator] 🔍 Deep searching: {query}")
        try:
            results = self.web_crawler.ddgs.text(query, max_results=5)
            results = list(results) if results else []

            if not results:
                return f"No results found for '{query}'"

            # Build a markdown-style intelligence brief (string only)
            timestamp = datetime.utcnow().isoformat() + "Z"
            lines = [f"# Intelligence Brief: {query}", "", f"_Generated: {timestamp}_", ""]

            for idx, r in enumerate(results, start=1):
                title = r.get("title", "No title")
                href = r.get("href", "")
                body = r.get("body", "")
                lines.append(f"## Source {idx}: {title}")
                if href:
                    lines.append(f"**URL:** {href}")
                if body:
                    lines.append("")
                    lines.append(body)
                lines.append("")

            brief_md = "\n".join(lines)

            # Store only in Chroma knowledge_graph so Norman can recall later
            if self.memory_manager is not None:
                try:
                    safe_query = "_".join(query.strip().split())[:80]
                    tags = ["intel_brief", safe_query]
                    self.memory_manager.add_knowledge(
                        content=brief_md,
                        source=f"intel_brief://{safe_query}",
                        tags=tags,
                        sentiment=0.0,
                    )
                    logging.info("[ResearchActuator] 🧠 Indexed brief in knowledge_graph")
                except Exception as e:
                    logging.warning(f"[ResearchActuator] Failed to add brief to memory: {e}")

            # Return concise summary to caller
            summary_lines = [f"Found {len(results)} results for '{query}':"]
            for r in results:
                title = r.get("title", "No title")
                href = r.get("href", "")
                summary_lines.append(f"- {title}: {href}")
            return "\n".join(summary_lines)
        except Exception as e:
            return f"Search failed: {str(e)}"

    async def deep_research(self, query: str) -> str:
        """
        Use the LangChain-based research agent to perform a deeper investigation.
        """
        logging.info(f"[ResearchActuator] 🧠 Deep research on: {query}")
        try:
            # This is synchronous and may be slow; run in a thread to not block the loop
            import asyncio
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, lambda: run_research_task(query)
            )

            # Optionally store the deep report into knowledge memory
            if self.memory_manager is not None:
                timestamp = datetime.utcnow().isoformat() + "Z"
                doc = (
                    f"# Deep Research Report: {query}\n\n"
                    f"_Generated: {timestamp}_\n\n"
                    f"{result}"
                )
                safe_query = "_".join(query.strip().split())[:80]
                self.memory_manager.add_knowledge(
                    content=doc,
                    source=f"deep_research://{safe_query}",
                    tags=["deep_research", safe_query],
                    sentiment=0.0,
                )
                logging.info("[ResearchActuator] 🧠 Indexed deep research report in knowledge_graph")

            return f"Deep research completed for '{query}'. Summary:\n\n{result[:800]}..."
        except Exception as e:
            logging.exception("[ResearchActuator] Deep research failed")
            return f"Deep research failed: {e}"
   
