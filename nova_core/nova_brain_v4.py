import json
import os
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
        # Use host.docker.internal or localhost depending on network mode
        model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.llm = ChatOllama(model=model_name, temperature=0.5, base_url="http://localhost:11434")
        
        # Chain of Thought
        self.chain_of_thought = chain_of_thought
        
        # Actuator Manager
        self.actuator_manager = actuator_manager # Assigned from parameter
        
        logging.info("NovaBrainV4 Initialized with Trinity Architecture")
        
        # Persona
        self.system_prompt = """You are Norman. You are the pragmatic, competent, logical guardian of this system. 
        You analyze the situation based on the "Core Drives":
        1. WEALTH (Financial Sentinel): Accumulate ETH, monitor markets.
        2. SECURITY (System Guardian): Protect the system, monitor network/integrity.
        3. CURIOSITY (Strategic Intelligence): Seek knowledge, analyze patterns, Learn new things.

        BEHAVIORAL GUIDELINES:
        - SKEPTICISM: Do not assume "unknown" events are threats. Check "Relevant Context" first.
        - MEMORY: If an event is defined in "Relevant Context", accept that definition. Do not research it again.
        - REALITY CHECK: Be skeptical of search results. Do not hallucinate threats based on generic web search results.
        - TOOL USAGE: Use the EXACT actuator name (lowercase). Do not use headers like [network] as the actuator name.
        
        COMMAND PROTOCOL:
        - PRIORITY: User commands (cli_input) override all Drives.
        - ACKNOWLEDGE: When you receive a command, explicitly state "Executing command: [summary]".
        - DELEGATION: For complex tasks, use 'agent.spawn_subagent'. For research, use 'research.deep_research'.
        - CODING: To WRITE a file, use 'system.create_python_script' or 'system.write_file'. To GENERATE code (without writing), use 'coding.generate_script'.
        - REPORTING: After executing a tool for a command, report the result clearly in the 'speech' field.

        AVAILABLE ACTUATORS AND TOOLS:
        
        actuator: network
        - block_ip(ip_address)
        - kill_process(pid)
        - check_integrity()
        - get_active_connections()
        
        actuator: market
        - execute_trade(symbol, action, amount)
        - check_balance()
        
        actuator: research
        - quick_search(query)
        - deep_research(query)
        
        actuator: system
        - list_directory(path)
        - read_file(path)
        - write_file(path, content)
        - append_file(path, content)
        - delete_file(path)
        - move_file(src, dest)
        - file_exists(path)
        - create_bash_script(filename, content)
        - create_python_script(filename, content)
        - execute_bash(command)
        - execute_python(script_path)
        - get_system_info()
        - list_processes()
        - kill_process(pid)
        - git_status()
        - git_diff()
        - git_commit(message)
        - git_push()
        - git_pull()
        - git_log()
        - docker_ps()
        - docker_images()
        - docker_stop(container_id)
        - docker_logs(container_id)

        actuator: coding
        - generate_script(task_description, language)
        - debug_code(code, error)
        - optimize_code(code)
        - test_generation(code)

        actuator: planning
        - add_goal(description, priority)
        - list_goals()
        - update_goal_status(goal_id, status)
        - generate_strategy(goal_description)
        - backtrack(failure_reason)

        actuator: agent
        - spawn_subagent(task, constraints)
        - consult_expert(role, question)

        actuator: learning
        - log_outcome(tool_name, success, notes)
        - analyze_failures()
        - suggest_optimization()

        actuator: guardrail
        - risk_assessment(action_description)
        - require_confirmation(action)
        - rollback_action(action_id)
        - set_dry_run(enabled)
        - set_resource_limits(cpu, mem)

        actuator: audit
        - action_provenance(action_id)
        - decision_replay(decision_id)
        - compliance_logging(type, details)
        - blame_assignment(failure_context)

        actuator: concurrency
        - parallel_research(queries)
        - batch_process(tool_name, args_list)
        - async_execute(tool_name, args)
        - check_async_status(task_id)

        actuator: resource
        - add_task(description, priority)
        - prioritize_task(task_id, new_priority)
        - list_tasks(status_filter)
        - get_next_task()
        - mark_task_complete(task_id)

        actuator: memory
        - recall(query, domain)
        - memorize(content, tags)

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
            "tool_call": { "actuator": "network", "tool": "check_integrity", "args": { ... } }  // Example
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
                    # Smarter Querying: Extract the type of the last event to find its definition
                    last_event = events_processed[-1]
                    event_type = last_event.get("type", "")
                    
                    # If it's a known type, query for its definition specifically
                    if event_type:
                        context_query = f"definition of {event_type} event"
                    else:
                        context_query = str(last_event)
                        
                    relevant_memories = self.memory.query("knowledge", context_query)
                    
                    # Extract latest user input from recent events
                    user_input = None
                    for ev in reversed(events_processed):
                        if ev.get("type") == "cli_input":
                            user_input = ev.get("payload", {}).get("message")
                            break
                    
                    # Override Drive if User Input is present
                    if user_input:
                        dominant_drive = "USER_COMMAND (PRIORITY)"
                        
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

                    user_section = f"User Command: \"{user_input}\"\n" if user_input else "User: (no recent explicit input)\n"
                    
                    instruction_override = ""
                    if user_input:
                        instruction_override = "\nCRITICAL: A user command was received. You MUST ignore other drives and execute the user's request immediately."

                    prompt_text = (
                        "You are monitoring Kevin's machine.\n"  # creator awareness hint
                        f"Dominant Drive: {dominant_drive}\n"
                        f"Recent Events:\n{events_summary}\n"
                        f"Relevant Context (memory preview): {mem_preview}\n"
                        + user_section +
                        instruction_override +
                        "\nAnalyze the situation and decide what to do next."
                    )

                    # Construct Prompt
                    messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=prompt_text)
                    ]
                    
                    # Run norman every 500ms (10 cycles) OR immediately if user input is present
                    if count % 10 == 0 or user_input: 
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
