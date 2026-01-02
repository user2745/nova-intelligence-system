import logging
from nova_core.memory_manager import ChromaMemoryManager

def preload_reality():
    """
    Preloads the ChromaDB with basic knowledge about reality, the system, and common events.
    """
    logging.basicConfig(level=logging.INFO)
    print("Initializing Memory Manager...")
    memory = ChromaMemoryManager()

    knowledge_base = [
        {
            "content": "The Nova Intelligence System is an autonomous cognitive architecture designed for wealth generation, security, and research.",
            "tags": ["self", "system", "identity"],
            "source": "preload"
        },
        {
            "content": "An 'unknown event type' in the system logs usually indicates a new perception source that hasn't been classified yet. It is not necessarily a threat but requires investigation.",
            "tags": ["system", "debugging", "events"],
            "source": "preload"
        },
        {
            "content": "The 'cli_input' event type represents direct commands or messages from the human user via the command line interface.",
            "tags": ["system", "io", "cli"],
            "source": "preload"
        },
        {
            "content": "Ethereum (ETH) is a decentralized, open-source blockchain with smart contract functionality. It is the primary asset for the Wealth drive.",
            "tags": ["crypto", "finance", "eth"],
            "source": "preload"
        },
        {
            "content": "The 'Security Drive' prioritizes system integrity, network safety, and process monitoring.",
            "tags": ["drives", "security", "core"],
            "source": "preload"
        },
        {
            "content": "The 'Curiosity Drive' seeks to expand the knowledge graph by researching unknown terms and exploring the environment.",
            "tags": ["drives", "curiosity", "core"],
            "source": "preload"
        },
        {
            "content": "If an event has no 'source' or 'payload', it might be a malformed packet or a ghost signal. Check the raw logs.",
            "tags": ["system", "error", "debugging"],
            "source": "preload"
        },
        {
            "content": "The 'system_stats' event contains real-time metrics about the machine's performance, including CPU usage, memory usage, and disk usage.",
            "tags": ["system", "metrics", "monitoring"],
            "source": "preload"
        },
        {
            "content": "The 'network_stats' event tracks active connections and data transfer rates (bytes sent/received).",
            "tags": ["network", "metrics", "monitoring"],
            "source": "preload"
        },
        {
            "content": "The 'market_data' event provides real-time prices for crypto assets like Ethereum (ETH) and Bitcoin (BTC).",
            "tags": ["market", "finance", "crypto"],
            "source": "preload"
        }
    ]

    print(f"Preloading {len(knowledge_base)} knowledge items...")
    
    for item in knowledge_base:
        memory.add_knowledge(
            content=item["content"],
            source=item["source"],
            tags=item["tags"]
        )
        print(f"Stored: {item['content'][:50]}...")

    print("Preload complete.")

if __name__ == "__main__":
    preload_reality()
