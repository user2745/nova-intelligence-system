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
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_WEB_TOOLS = True
except ImportError:
    HAS_WEB_TOOLS = False
    print("[WARNING] Web scraping tools not available (missing requests/bs4)")

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False
    print("[WARNING] Web search tool not available (missing ddgs)")

try:
    from langchain_ollama import ChatOllama
    from langchain.tools import tool
    from langchain.agents import create_react_agent 
    from langchain_core.ms import BaseMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    print("[WARNING] LangChain tools not available")


# ----------------------
# Tools
# ----------------------

if HAS_WEB_TOOLS and HAS_DDGS:
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
else:
    # Dummy functions if dependencies not available
    def web_scrape(url: str) -> str:
        return "Web scraping not available - missing dependencies"
    
    def web_research(query: str) -> str:
        return "Web research not available - missing dependencies"


# ----------------------
# OS Navigation & File Tools
# ----------------------

# Define decorator or stub it
if HAS_LANGCHAIN:
    tool_decorator = tool
else:
    def tool_decorator(func):
        return func

@tool_decorator
def list_directory(path: str) -> str:
    """List all files and directories in the given path.

    Use this to explore the file system and see what's available.
    """
    try:
        expanded_path = os.path.expanduser(path)
        if not os.path.isdir(expanded_path):
            return f"Error: {path} is not a valid directory."
        
        items = []
        for item in sorted(os.listdir(expanded_path)):
            item_path = os.path.join(expanded_path, item)
            if os.path.isdir(item_path):
                items.append(f"[DIR] {item}")
            else:
                items.append(f"[FILE] {item}")
        
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {e}"


@tool_decorator
def read_file(path: str) -> str:
    """Read and return the contents of a file.

    Use this to view file contents before deciding to modify or execute.
    """
    try:
        expanded_path = os.path.expanduser(path)
        if not os.path.isfile(expanded_path):
            return f"Error: {path} is not a valid file."
        
        with open(expanded_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Limit output to prevent context bloat
        if len(content) > 10000:
            return f"File is {len(content)} characters (truncated to first 10000):\n\n{content[:10000]}\n\n... (truncated)"
        return content
    except Exception as e:
        return f"Error reading file: {e}"


@tool_decorator
def file_exists(path: str) -> str:
    """Check if a file or directory exists at the given path."""
    try:
        expanded_path = os.path.expanduser(path)
        exists = os.path.exists(expanded_path)
        is_file = os.path.isfile(expanded_path) if exists else False
        is_dir = os.path.isdir(expanded_path) if exists else False
        
        if not exists:
            return f"Path does not exist: {path}"
        elif is_file:
            return f"Path is a file: {path}"
        elif is_dir:
            return f"Path is a directory: {path}"
    except Exception as e:
        return f"Error checking path: {e}"


@tool_decorator
def create_bash_script(filename: str, content: str) -> str:
    """Create a bash script with the given filename and content.

    The script will be saved in the current working directory.
    Content should be valid bash code starting with #!/bin/bash (optional, will be added if missing).
    """
    try:
        # Ensure shebang
        if not content.strip().startswith("#!"):
            content = "#!/bin/bash\n" + content
        
        filepath = os.path.expanduser(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable
        os.chmod(filepath, 0o755)
        
        return f"Bash script created successfully: {filepath}"
    except Exception as e:
        return f"Error creating bash script: {e}"


@tool_decorator
def create_python_script(filename: str, content: str) -> str:
    """Create a python script with the given filename and content.

    The script will be saved in the current working directory.
    Content should be valid Python code starting with #!/usr/bin/env python3 (optional, will be added if missing).
    """
    try:
        # Ensure shebang
        if not content.strip().startswith("#!"):
            content = "#!/usr/bin/env python3\n" + content
        
        filepath = os.path.expanduser(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable
        os.chmod(filepath, 0o755)
        
        return f"Python script created successfully: {filepath}"
    except Exception as e:
        return f"Error creating python script: {e}"


@tool_decorator
def execute_bash(command: str) -> str:
    """Execute a bash command or bash script and return the output.

    Pass either:
    - A direct command: "ls -la /tmp"
    - A script path: "/path/to/script.sh"
    
    Use this to run system commands and scripts.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        
        if result.returncode != 0:
            output += f"\n[Return code: {result.returncode}]"
        
        # Limit output size
        if len(output) > 5000:
            return f"Output is {len(output)} characters (truncated to first 5000):\n\n{output[:5000]}\n\n... (truncated)"
        
        return output if output else "[Command executed with no output]"
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out (30 seconds limit)."
    except Exception as e:
        return f"Error executing bash command: {e}"


@tool_decorator
def execute_python(script_path: str) -> str:
    """Execute a python script and return the output.

    Pass the path to a .py file to execute it.
    Use this to run Python scripts created with create_python_script.
    """
    try:
        expanded_path = os.path.expanduser(script_path)
        if not os.path.isfile(expanded_path):
            return f"Error: {script_path} is not a valid file."
        
        result = subprocess.run(
            ["python3", expanded_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        
        if result.returncode != 0:
            output += f"\n[Return code: {result.returncode}]"
        
        # Limit output size
        if len(output) > 5000:
            return f"Output is {len(output)} characters (truncated to first 5000):\n\n{output[:5000]}\n\n... (truncated)"
        
        return output if output else "[Script executed with no output]"
    except subprocess.TimeoutExpired:
        return "Error: Script execution timed out (30 seconds limit)."
    except Exception as e:
        return f"Error executing python script: {e}"


# ----------------------
# Agent construction
# ----------------------

def build_agent() -> Any:
    """Create a LangChain 1.x agent that uses our tools."""
    if not HAS_LANGCHAIN:
        raise RuntimeError("LangChain dependencies not installed. Cannot build agent.")
    
    # Chat model backed by Ollama
    model = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.1"),  # make sure this model exists in `ollama list`
        temperature=0.2,
        stream=False,     # <- ADD THIS

    )

    tools = [
        web_scrape,
        web_research,
        list_directory,
        read_file,
        file_exists,
        create_bash_script,
        create_python_script,
        execute_bash,
        execute_python,
    ]

    system_prompt = textwrap.dedent(
        """
        You are a meticulous research and systems assistant.

        You have access to these tools:
        
        WEB TOOLS:
        - web_scrape: scrape the visible text from a specific URL
        - web_research: run a DuckDuckGo search and get result snippets
        
        OS & FILE TOOLS:
        - list_directory: explore filesystem and view directory contents
        - read_file: read file contents
        - file_exists: check if a file or directory exists
        
        SCRIPT TOOLS:
        - create_bash_script: create and save a bash script
        - create_python_script: create and save a python script
        - execute_bash: execute bash commands or scripts
        - execute_python: execute python scripts

        Guidelines:
        - For broad questions, start with web_research to gather context.
        - When a specific source looks important, use web_scrape on its URL.
        - Synthesize information from multiple sources; don't just copy a single snippet.
        - Be explicit about uncertainty and contradictions between sources.
        - When creating scripts, ensure they are well-documented and handle errors gracefully.
        - Always verify file paths exist before trying to read or execute them.
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


if __name__ == "__main__":
    print("=" * 80)
    print("NOVA RESEARCH AGENT - TOOL DEMONSTRATION")
    print("=" * 80)
    
    if HAS_LANGCHAIN:
        # Test the agent with a sample task
        test_task = "List the contents of the current directory, then create a simple bash script that prints a greeting."
        print(f"\n[LangChain Agent Mode]")
        print(f"Running task: {test_task}")
        print("-" * 80)
        try:
            result = run_research_task(test_task)
            print("\nAgent Output:")
            print(result)
        except Exception as e:
            print(f"Error running agent: {e}")
    else:
        print("\n[Demo Tool Mode - LangChain not available]")
        print("\nAvailable tools:")
        print("  ✓ list_directory - explore filesystem")
        print("  ✓ read_file - read file contents")
        print("  ✓ file_exists - check file paths")
        print("  ✓ create_bash_script - create bash scripts")
        print("  ✓ create_python_script - create python scripts")
        print("  ✓ execute_bash - run bash commands")
        print("  ✓ execute_python - run python scripts")
        
        if not HAS_WEB_TOOLS:
            print("  ✗ web_scrape - not available (missing requests/bs4)")
        if not HAS_DDGS:
            print("  ✗ web_research - not available (missing ddgs)")
        
        print("\n" + "-" * 80)
        print("TOOL DEMONSTRATION:")
        print("-" * 80)
        
        # Demo 1: List directory
        print("\n[1] Listing current directory:")
        result = list_directory(".")
        print(result[:500] + ("..." if len(result) > 500 else ""))
        
        # Demo 2: File exists check
        print("\n[2] Checking if 'requirements.txt' exists:")
        result = file_exists("requirements.txt")
        print(result)
        
        # Demo 3: Create a bash script
        print("\n[3] Creating a bash script:")
        script_content = '''
echo "Hello from Nova Agent!"
echo "Current directory: $(pwd)"
echo "Date: $(date)"
'''
        result = create_bash_script("demo_script.sh", script_content)
        print(result)
        
        # Demo 4: Execute the bash script
        print("\n[4] Executing the bash script:")
        result = execute_bash("bash ./demo_script.sh")
        print(result)
        
        # Demo 5: Create and run a Python script
        print("\n[5] Creating and executing a Python script:")
        python_content = '''
import os
print("Python Execution Demo")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {len(os.listdir('.'))}")
'''
        result = create_python_script("demo_script.py", python_content)
        print(result)
        
        result = execute_python("demo_script.py")
        print(result)
        
        # Clean up
        print("\n[6] Cleaning up demo scripts:")
        execute_bash("rm -f demo_script.sh demo_script.py")
        print("Demo scripts removed.")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
