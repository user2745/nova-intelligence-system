#!/usr/bin/env python
"""
Research agent using LangChain 1.x + LangGraph 1.x + Ollama.

- Uses ChatOllama as the LLM (model "deepseek-llm" by default).
- Provides two tools:
    - web_scrape(url): scrape visible text from a web page
    - web_research(query): DuckDuckGo search, returns top snippets
- Runs a single research task from __main__ and prints the final answer.
"""

import textwrap
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage


# ----------------------
# Tools
# ----------------------

@tool
def web_scrape(url: str) -> str:
    """Scrape visible text content from the given URL.

    Use this when you have a specific page you want to read in more detail.
    """
    try:
        clean_url = url.strip().replace("\n", "").replace("\r", "")
        resp = requests.get(clean_url, timeout=15)
    except Exception as e:
        return f"Failed to fetch URL {url}: {e}"

    if resp.status_code != 200:
        return f"Failed to retrieve webpage content. HTTP status: {resp.status_code}"

    soup = BeautifulSoup(resp.text, "html.parser")
    # Basic cleanup: remove script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse whitespace and limit size so we don't blow up context
    lines = [line.strip() for line in text.splitlines()]
    text_clean = "\n".join(line for line in lines if line)
    # Limit to first ~8000 characters
    return text_clean[:8000]


@tool
def web_research(query: str) -> str:
    """Search the web (DuckDuckGo) and return a small list of relevant results.

    Use this to gather high-level information and links about a topic.
    """
    try:
        results: List[Dict[str, Any]] = []
        with DDGS() as ddgs:
            for res in ddgs.text(query, max_results=5):
                results.append(res)

        if not results:
            return "No relevant information found."

        formatted = []
        for r in results:
            title = r.get("title", "No title")
            snippet = r.get("body", "No snippet")
            link = r.get("href", "No link")
            formatted.append(
                f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n"
            )

        return "\n".join(formatted)

    except Exception as e:
        return f"An error occurred during web research: {e}"


# ----------------------
# Agent construction
# ----------------------

def build_agent() -> Any:
    """Create a LangChain 1.x agent that uses our tools."""
    # Chat model backed by Ollama
    model = ChatOllama(
        model="llama3.1",  # make sure this model exists in `ollama list`
        temperature=0.2,
        stream=False,     # <- ADD THIS

    )

    tools = [web_scrape, web_research]

    system_prompt = textwrap.dedent(
        """
        You are a meticulous research assistant.

        You have access to these tools:
        - web_scrape: scrape the visible text from a specific URL
        - web_research: run a DuckDuckGo search and get result snippets

        Guidelines:
        - For broad questions, start with web_research to gather context.
        - When a specific source looks important, use web_scrape on its URL.
        - Synthesize information from multiple sources; don't just copy a single snippet.
        - Be explicit about uncertainty and contradictions between sources.
        - At the end, provide a clear, structured summary for the user.
        """
    ).strip()

    # LangChain v1-style agent (internally uses LangGraph)
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )
    return agent


def run_research_task(task: str) -> str:
    """Run a single research task and return the final answer as text."""
    agent = build_agent()

    # The agent expects a "messages" state: list of role/content pairs or BaseMessages
    state = agent.invoke(
        {"messages": [("user", task)]}
    )

    messages: List[BaseMessage] = state["messages"]
    if not messages:
        return "Agent returned no messages."

    final_msg = messages[-1]
    content = final_msg.content

    # content can be a plain string or a list of content parts
    if isinstance(content, str):
        return content
    return str(content)
