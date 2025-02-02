# ucp_pubsub.py  
from rx.subject import Subject, BehaviorSubject  
from ucp import UCPClient, UCPServer
from datetime import datetime
import asyncio
import os
import json

class UCPPubSub:  
    def __init__(self):  
        # Internal RxPy streams
        self.command_stream = Subject()
        self.context_stream = BehaviorSubject({
        "status": "booting",
        "system": {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "my_cpu_usage": 0.0,
            "my_memory_usage": 0.0
        },
        "wallet": {
            "balance": 0.0,
            "address": "",
            "transaction_count": 0,
            "gas_fee": 0.0
        },
        "time": datetime.now().isoformat()
        })

        self.state_file = "nova-state.json"
        self.state_stream = BehaviorSubject(self._load_state());

        self.response_stream = Subject()
        self.transaction_stream = Subject()

        # External UCPClient for Flutter communication
        self.ucp_client = UCPClient(device_id="NovaCore", broker_address="localhost")
        self.ucp_client.connect()

        # Subscribe to incoming commands
        self.ucp_client.subscribe("ucl/commands/NovaCore")

        # Subscribe to incoming state messages (distributed sync)
        self.ucp_client.subscribe("ucl/state/NovaCore");

        # Forward commands from UCPClient to internal streams
        self.ucp_client.set_message_handler(self._handle_incoming_message)

        # Forward responses from internal streams to UCPClient
        self.response_stream.subscribe(
            lambda resp: self.ucp_client.publish("ucl/responses/NovaCore", resp)
        )

        # Subscribe to state updates and persist them
        self.state_stream.subscribe(self._persist_state)





        # Broadcast initial state after 3 seconds (gives time to sync if others exist)
        asyncio.create_task(self._broadcast_initial_state())

        # Start heartbeat
        self.ucp_client.start_heartbeat(interval=10)

    def _handle_incoming_message(self, topic, message):
        try:
            command = json.loads(message)
            if topic == "ucl/state/NovaCore":
                print(f"📡 Received state update: {message}")
                self._merge_state(command)
            elif topic == "ucl/commands/NovaCore":
                print(f"📡 Received command: {command}")
                self.command_stream.on_next(command)
            elif topic == "ucl/task_queue/NovaCore":
                print(f"📡 Received task queue update: {command}")
                self.emit_context({"task_queue": command})
            else:
                print(f"Unknown topic: {topic}")
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
  

    def emit_command(self, command: dict):  
        self.command_stream.on_next(command)  

    # ucp_pubsub.py
    def emit_context(self, context: dict):
        current_context = self.context_stream.value
        merged_context = {**current_context, **context}  # Merge dictionaries
        self.context_stream.on_next(merged_context)

    def emit_response(self, response: dict):  
        self.response_stream.on_next(response)  

    def emit_state(self, state_update: dict):
        """Update state only if something changed and publish to UCP for global sync."""
        current_state = self.state_stream.value
        timestamp = datetime.now().isoformat()

        # Only store new values, preventing unnecessary updates
        updated_state = {}
        for key, value in state_update.items():
            if key not in current_state or current_state[key] != value:
                updated_state[key] = {"value": value, "timestamp": timestamp}

        if updated_state:  # Only emit if something actually changed
            self.state_stream.on_next({**current_state, **updated_state})
            self.ucp_client.publish("ucl/state/NovaCore", json.dumps(updated_state))


    def _merge_state(self, incoming_update):
        """Merge incoming state updates from other Nova instances."""
        current_state = self.state_stream.value
        merged_state = {**current_state}
        timestamp = datetime.now().isoformat()

        for key, value in incoming_update.items():
            # Ensure value is in the expected format
            if not isinstance(value, dict):
                value = {"value": value, "timestamp": timestamp}  # Wrap it properly

            # Merge state, keeping only newer timestamps
            if key not in merged_state or value["timestamp"] > merged_state[key]["timestamp"]:
                merged_state[key] = value

        print(f"🔄 Merging state: {merged_state}")
        self.state_stream.on_next(merged_state)

    
    def _load_state(self):
        """Load state from a local file if it exists, otherwise return default."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass  # Corrupt file, return default

        return {}  # Default state

    def _persist_state(self, state):
        """Persist the current state to local storage."""
        with open(self.state_file, "w") as f:
            json.dump(state, f)
    
    async def _broadcast_initial_state(self):
        """Broadcast initial state if no other device provides it first."""
        await asyncio.sleep(3)  # Wait for possible incoming state sync

        if not self.state_stream.value:
            print("⚡ No state detected. Seeding new state.")
            self.emit_state({
                "initialized": True,
                "mood": "neutral",
                "last_action": "idle",
                "task_queue": [],
                "system_health": {"cpu_usage": 0, "memory_usage": 0},
                "timestamp": datetime.now().isoformat(),
            })