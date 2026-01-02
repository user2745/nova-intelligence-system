import os
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from speak_tool import speak


def build_speak_agent():
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "phi4"),
        temperature=0.2,
        stream=False
    )

    system_prompt = """
    You are a speech agent. 
    Your job is to convert text into speech using the 'speak' tool.
    Whenever the user asks you to 'speak', 'say', 'read', or 'pronounce'
    you must call the tool.
    """

    return create_agent(
        model=llm,
        tools=[speak],
        system_prompt=system_prompt.strip(),
    )


def run_speak(text: str):
    agent = build_speak_agent()
    result = agent.invoke({"messages": [("user", f"Speak this: {text}")]} )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    # Test the speak agent
    print("Testing Piper TTS speak agent...")
    run_speak("""
    Based on the web research results: 
        Current Situation: The conflict in Sudan has escalated into a full-blown civil war 
    """)
