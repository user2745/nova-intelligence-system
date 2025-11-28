import json
import aiohttp
import asyncio
import time
import logging
from rx.subject import Subject
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from nova_core.memory_manager import ChromaMemoryManager

from nova_core.DGOP.drives.DriveManager import DriveManager

# Rich Imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# Custom Theme for norman
custom_theme = Theme({
    "norman": "cyan",
    "system": "dim white",
    "alert": "bold red",
    "wealth": "gold1",
    "security": "bold blue",
    "curiosity": "magenta"
})
console = Console(theme=custom_theme)

class NovaBrainV4:
    """
    The brain manages the cognitive cycle, sleep cycle, and three forms of memory:
    working, declarative and procedural. This version runs a continuous conscious loop,
    processing perception, evaluating rules, invoking LLM inferences, and emitting actions.
    """
    def __init__(self, ucp: Subject, working_memory, declarative_memory,
                 procedural_memory, situational_awareness, chain_of_thought,
                 real_time_queue, actuator_manager, memory_manager=None):
        self.ucp = ucp
        self.running = True
        console.print("[system]Initializing NovaBrainV4...[/system]")

        # Memory modules
        self.working_memory = working_memory
        self.declarative_memory = declarative_memory
        self.procedural_memory = procedural_memory
        self.situational_awareness = situational_awareness
        
        # Unified Memory (Trinity)
        if memory_manager:
            self.memory = memory_manager
        else:
            self.memory = ChromaMemoryManager()
        
        # The Will (DGOP)
        self.drive_manager = DriveManager()

        # Input stream
        self.real_time_queue = real_time_queue # Assigned from parameter
        
        # LLM (The Soul)
        self.llm = ChatOllama(model="llama3.1", temperature=0.5)
        
        # Chain of Thought
        self.chain_of_thought = chain_of_thought
        
        # Actuator Manager
        self.actuator_manager = actuator_manager # Assigned from parameter
        
        logging.info("NovaBrainV4 Initialized with Trinity Architecture")
        
        # Persona
        self.system_prompt = """You are Norman norman. You are the pragmatic, competent, logical guardian of this system. 
        You analyze the situation based on the "Core Drives":
        1. WEALTH (Financial Sentinel): Accumulate ETH, monitor markets.
        2. SECURITY (System Guardian): Protect the system, monitor network/integrity.
        3. CURIOSITY (Strategic Intelligence): Seek knowledge, analyze patterns, Learn new things.

        You have access to the following TOOLS (Actuators):
        - network.block_ip(ip_address): Block a suspicious IP.
        - network.kill_process(pid): Terminate a process.
        - network.check_integrity(): Check system integrity.
        - network.get_active_connections(): Get active network connections.
        - market.execute_trade(symbol, action, amount): Buy/Sell crypto.
        - market.check_balance(): Check wallet.
        - research.quick_search(query): Search the web.
        - research.deep_research(query): Perform an in-depth research task.

        Your Goal:
        1. Analyze the 'Context' (Recent Events).
        2. Determine the 'Dominant Drive' (Which goal is most urgent?).
        3. Formulate a 'Decision' (What to do?).
        4. (Optional) EXECUTE a tool if action is needed.

        Output Format (JSON):
        {
            "analysis": "Brief analysis of the situation.",
            "decision": "Strategic decision.",
            "speech": "What you say to the user (concise, norman persona).",
            "tool_call": { "actuator": "name", "tool": "name", "args": { ... } }  // OPTIONAL: Only if acting.
        }

        Your output MUST be ONLY a JSON object. 
        NO prose before or after. 
        NO code blocks. 
        If you are uncertain, output the safest possible JSON.

        """

        # High-level cognitive processes
        
        

        # Low-level cognitive processes
        

        # Subscribe to context updates
        self.ucp.subscribe(self._on_context_event)

    def _on_context_event(self, event: dict):
        """
        Handle incoming context: update memories and enqueue thought blocks.
        Called immediately on every perception or command event.
        """
        payload = event

        # If this is user input, tag it clearly
        if payload.get("type") == "cli_input":
            msg = payload.get("payload", {}).get("message", "")
            logging.info(f"[Brain] Received user command: {msg}")
            # Optionally store in working memory under a special key
            self.working_memory.write({"type": "user_input", "message": msg})
            # And push a thought block so it's processed immediately
            self.chain_of_thought.add_thought({
                "timestamp": time.time(),
                "thought": {"user_message": msg}
            })

        # 1. Update Working Memory
        try:
            self.working_memory.write(payload)
        except Exception as e:
            logging.warning(f"WorkingMemory update failed: {e}")

        # 2. Log to Declarative Memory (Legacy)
        try:
            self.declarative_memory.add_episode(payload)
        except Exception as e:
            logging.warning(f"DeclarativeMemory add_episode failed: {e}")
            
        # 3. Log to Unified Memory (Episodic Stream)
        try:
            # Flatten metadata for ChromaDB (no nested dicts allowed)
            safe_metadata = {
                "type": payload.get("type", "unknown"),
                "source": payload.get("source", "system"),
                "timestamp": payload.get("timestamp", time.time())
            }
            
            self.memory.add_episodic(
                text=str(payload),
                type=str(payload.get("type", "perception")),
                domain="general"
            )
        except Exception as e:
            logging.warning(f"ChromaMemory add_episodic failed: {e}")

        # 4. Update Situational Model
        try:
            self.situational_awareness.add_event(name="external_context", payload=payload)
            # logging.info(f"SituationalModel updated with event: {payload}")
        except Exception as e:
            logging.warning(f"SituationalModel merge_event failed: {e}")

    async def cognitive_cycle(self):
        """
        Main conscious loop running at ~50ms intervals.
        Processes queued thought blocks, applies rules, calls LLMs, and emits actions.
        """
        console.print("[system]Starting cognitive cycle...[/system]")
        count = 0
        while self.running:
            cycle_start = time.time()
            # logging.debug(f"[Brain] Cognitive cycle iteration {count}")
            count += 1
            
            # Step 1: Process real-time events
            events_processed = []
            while not self.real_time_queue.is_empty():
                event = await self.real_time_queue.dequeue()
                # console.print(f"[system]Processing event: {event['type'] if 'type' in event else 'unknown'}[/system]")
                self._on_context_event(event)
                events_processed.append(event)

            # Step 2: Update Drives & Trigger norman
            if events_processed:
                try:
                    # Update Drives
                    current_context = self.situational_awareness.current_situation
                    dominant_drive = self.drive_manager.update_drives(current_context)
                    
                    # Retrieve Context
                    context_query = str(events_processed[-1])
                    relevant_memories = self.memory.query("knowledge", context_query)
                    
                    # Extract latest user input if present
                    user_input = None
                    try:
                        wm_snapshot = getattr(self.working_memory, "memory", None)
                        if isinstance(wm_snapshot, list) and wm_snapshot:
                            for item in reversed(wm_snapshot):
                                if isinstance(item, dict) and item.get("type") == "user_input":
                                    user_input = item.get("message")
                                    break
                    except Exception as e:
                        logging.debug(f"[Brain] Failed to read last user_input from working_memory: {e}")
                    
                    # Compact summaries for the LLM
                    recent_events = events_processed[-5:]
                    event_lines = []
                    for ev in recent_events:
                        etype = ev.get("type", "unknown")
                        src = ev.get("source", "unknown")
                        payload = ev.get("payload") or {}
                        line = f"- type={etype}, source={src}, payload_keys={list(payload.keys())}"
                        event_lines.append(line)

                    events_summary = "\n".join(event_lines) if event_lines else "(none)"

                    # Trim relevant memories to a short string
                    mem_preview = str(relevant_memories)
                    if len(mem_preview) > 800:
                        mem_preview = mem_preview[:800] + "..."

                    user_section = f"User: \"{user_input}\"\n" if user_input else "User: (no recent explicit input)\n"

                    prompt_text = (
                        "You are monitoring Kevin's machine.\n"  # creator awareness hint
                        f"Dominant Drive: {dominant_drive}\n"
                        f"Recent Events:\n{events_summary}\n"
                        f"Relevant Context (memory preview): {mem_preview}\n"
                        + user_section +
                        "Analyze the situation and decide what to do next."
                    )

                    # Construct Prompt
                    messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=prompt_text)
                    ]
                    
                    if count % 10 == 0: # Run norman every 500ms (10 cycles * 50ms/cycle)
                        # Call LLM
                        # console.print("[system]norman is calculating...[/system]")
                        try:
                            response = self.llm.invoke(messages)
                            logging.info(f"[Brain] norman's response: {response}")
                            decision = self.sanatize(response.content)
                        except Exception as e:
                            logging.error(f"[Brain] Cognitive Error: {e}")
                            decision = {
                                "analysis": "The internal model failed to structure its thoughts.",
                                "decision": "Proceed with caution.",
                                "speech": "I am currently analyzing the system's performance and looking into new technological developments as requested by my user. If you have a specific topic of interest, please let me know so I can focus my research accordingly.",
                                "tool_call": None
                            }

                        # Display Output
                        self._display_thought(decision, dominant_drive)
                        await self._execute_decision(decision)

                        try:
                            self.memory.add_episodic(
                                text=f"Analysis: {decision['analysis']} | Decision: {decision['decision']}",
                                type="thought",
                                domain="general",
                                drive=dominant_drive
                            )
                        except Exception as e:
                            logging.warning(f"ChromaMemory add_episodic failed: {e}")

                        # 5. Enqueue Thought Block
                        try:
                            self.chain_of_thought.add_thought({
                                'timestamp': time.time(),
                                'thought': f"Analysis: {decision['analysis']} | Decision: {decision['decision']}",
                            })
                        except Exception as e:
                            logging.warning(f"ChainOfThought add_thought failed: {e}")
                    
                except Exception as e:
                    logging.error(f"[Brain] Cognitive Error: {e}")

            # Maintain cycle timing
            elapsed = time.time() - cycle_start
            await asyncio.sleep(max(0.05 - elapsed, 0))

    def sanatize(self, text: str):
        """
        Sanatize the text to remove any special characters and convert to JSON.
        """
        text = text.strip()

        # If it's already valid JSON
        try:
            return json.loads(text)
        except:
            pass

        # Try to extract JSON inside surrounding text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except:
                pass

        # Hard fallback
        return {
            "analysis": "Model returned invalid JSON.",
            "decision": "Proceed cautiously.",
            "speech": "I am stabilizing my internal cognitive structure.",
            "tool_call": None
        }

    
    async def _execute_decision(self, decision: dict):
        logging.info(f"[Brain] Executing decision: {decision['decision']}")

        tool_call = decision.get("tool_call")
        if not tool_call:
            return

        # Allow single object OR list
        if isinstance(tool_call, list):
            calls = tool_call
        else:
            calls = [tool_call]

        for call in calls:
            actuator = call.get("actuator")
            tool = call.get("tool")
            args = call.get("args", {}) or {}

            if actuator and tool:
                logging.info(f"[Brain] 🛠️ Invoking Tool: {actuator}.{tool} with args={args}")
                result = await self.actuator_manager.execute_tool(actuator, tool, **args)

                # Feedback loop
                self.memory.add_episodic(
                    text=f"Tool Execution Result ({tool}): {result}",
                    type="action_result",
                    domain="system"
                )

                console.print(
                    Panel(
                        f"[bold green]Action Executed:[/bold green] {actuator}.{tool}\n[dim]{result}[/dim]",
                        title="[norman]Actuator Output[/norman]",
                        border_style="green",
                    )
                )

    def _display_thought(self, decision: dict, drive: str):
        """Render norman's thought process nicely."""
        
        drive_color = "white"
        if drive == "wealth": drive_color = "wealth"
        elif drive == "security": drive_color = "alert"
        elif drive == "curiosity": drive_color = "curiosity"
        
        content = f"[bold]Analysis:[/bold] {decision['analysis']}\n"
        content += f"[bold]Decision:[/bold] {decision['decision']}\n"
        
        if "speech" in decision and decision["speech"]:
             content += f"\n[norman]🗣️ \"{decision['speech']}\"[/norman]"
        
        panel = Panel(
            content,
            title=f"[norman]Norman[/norman] | Drive: [{drive_color}]{drive.upper()}[/{drive_color}]",
            border_style="cyan"
        )
        console.print(panel)

    async def shutdown(self):
        """Stop the cognitive loop cleanly."""
        self.running = False
