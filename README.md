# Nova Intelligence System (v0.4 Alpha)

![Status: Experimental](https://img.shields.io/badge/Status-Experimental-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-blue)
![Powered By: Ollama](https://img.shields.io/badge/Powered%20By-Ollama-white)

**A Local-First, Autonomous Cognitive Architecture.**

Nova is a continuously conscious AI agent designed to run on your own hardware. It maintains real-time awareness, processes multi-stream data, and executes complex tasks through a plugin-style actuator system. It is designed to be private, self-healing, and capable of deep research and system monitoring without relying on cloud APIs.

> **⚠️ DISCLAIMER**: This is an **experimental research prototype**. The agent has autonomous capabilities (file editing, web research, system monitoring). Run this in a controlled environment (like the provided Docker container). The authors are not responsible for actions taken by the agent.

---

## 🏗️ Architecture

Nova operates as a closed loop of **Perception**, **Cognition**, and **Action**, grounded by a local Vector Memory.

```mermaid
graph TD
    User[User / World] -->|CLI / Events| Perceptions
    Perceptions -->|Sensory Input| Brain[Nova Brain v4]
    
    subgraph "Host Machine"
        Ollama[Ollama (LLM)]
    end

    subgraph "Nova Container"
        Brain <-->|Recall/Store| Memory[ChromaDB Vector Store]
        Brain <-->|Inference| Ollama
        
        Brain -->|Decide| Actuators
        
        subgraph "Actuators (The Body)"
            Research[Research Agent] -->|DuckDuckGo| Internet
            Coding[Coding Agent] -->|Write/Debug| Filesystem
            System[System Snitch] -->|Monitor| Host Resources
            Speak[Speak Agent] -->|TTS| Audio
        end
    end
```

---

## 🚀 Quick Start

### Prerequisites
1.  **Docker & Docker Compose** installed.
2.  **[Ollama](https://ollama.com/)** installed and running on the host machine.
3.  **Pull a Model**:
    ```bash
    ollama pull llama3.1  # or phi3, mistral, etc.
    ```

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/user2745/nova-intelligence-system.git
    cd nova-intelligence-system
    ```

2.  **Configure Environment**:
    Copy the example configuration and edit it.
    ```bash
    cp .env.example .env
    ```
    
    Edit `.env` to set your preferred model and (optional) private keys:
    ```ini
    # .env
    OLLAMA_MODEL=llama3.1  # Must match the model you pulled
    WALLET_PRIVATE_KEY=... # Optional: For blockchain monitoring
    ```

3.  **Launch**:
    Start the system in detached mode.
    ```bash
    docker-compose up -d --build
    ```

4.  **Monitor**:
    Watch the agent's "thought stream" in the logs.
    ```bash
    docker-compose logs -f
    ```

---

## 🧠 Features

*   **Dynamic LLM Backend**: Switch between `llama3`, `phi3`, `mistral`, or `deepseek` instantly via environment variables.
*   **Continuous Consciousness**: Maintains a coherent state across time; doesn't just wait for user input.
*   **Deep Research**: Can autonomously formulate search queries, scrape websites, and synthesize reports.
*   **Self-Correction**: Includes robust error handling to recover from LLM hallucinations (e.g., malformed tool calls).
*   **Blockchain-Verified Thoughts**: (Experimental) Cryptographically verifies thought chains for auditability.

---

## � Interaction & Capabilities

Nova is controlled via natural language through the CLI (or future interfaces). It maps your intent to specific "Actuators".

| Capability | Example Command | Underlying Tool |
| :--- | :--- | :--- |
| **Research** | *"Research the latest CVEs for Nginx and summarize them."* | `research_actuator` (DuckDuckGo + Scraper) |
| **System Control** | *"Check disk usage and list active Docker containers."* | `system_snitch` (Shell Access) |
| **Coding** | *"Write a Python script to parse a CSV file and debug it."* | `coding_actuator` |
| **Memory** | *"Remember that the project deadline is Friday."* | `memory_manager` (Vector Store) |
| **Planning** | *"Create a step-by-step plan to secure this server."* | `planning_actuator` |
| **Audit** | *"Why did you decide to run that command?"* | `audit_actuator` |

---

## �📂 Project Structure

*   `nova_core/`: The "Brain" logic, memory management, and cognitive cycles.
*   `actuators/`: The "Hands" of the system (Research, Coding, Audit, etc.).
*   `agents/`: Specialized sub-agents (LangChain/LangGraph implementations).
*   `perceptions/`: Input streams (System monitoring, Time, Wallet watching).
*   `working_memory_db/`: Persistent Vector Store (ChromaDB).

---

## 🤝 Contributing

This project is Open Source (MIT). We welcome contributions, especially in:
*   **New Actuators**: Add capabilities like Email, Slack, or Home Assistant integration.
*   **Memory Optimization**: Improving how the agent retrieves context.
*   **Swarm Logic**: Enabling multi-agent coordination.

## License

MIT License. See `LICENSE` file for details.
