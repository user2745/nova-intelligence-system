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
        self.context_stream = Subject() # Default empty context

        self.intent_stream = Subject()

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

        # Subscribe to incoming context messages
        self.ucp_client.subscribe("ucl/task_queue/NovaCore");

        self.ucp_client.subscribe("ucl/intents/NovaCore");


        # Forward commands from UCPClient to internal streams
        self.ucp_client.set_message_handler(self._handle_incoming_message)

        # Forward responses from internal streams to UCPClient
        self.response_stream.subscribe(
            lambda resp: self.ucp_client.publish("ucl/responses/NovaCore", resp)
        )

        # Subscribe to state updates and persist them
        self.state_stream.subscribe(self._persist_state)

        # # Broadcast initial state after 3 seconds (gives time to sync if others exist)

        # Start heartbeat
        self.ucp_client.start_heartbeat(interval=10)

    # This takes globally emitted messages and forwards them to the appropriate internal streams
    def _handle_incoming_message(self, topic, message):
        try:
            command = json.loads(message)
            if topic == "ucl/state/NovaCore":
                print(f"📡 Received state update: {message}")
                self.state_stream.on_next(command)
            elif topic == "ucl/commands/NovaCore":
                print(f"📡 Received command: {command}")
                self.command_stream.on_next(command)
            elif topic == "ucl/task_queue/NovaCore":
                print(f"📡 Received task queue update: {command}")
                self.emit_context({"task_queue": command})
            elif topic == "ucl/intents/NovaCore":
                print(f"📡 Received intent: {command}")
                self.intent_stream.on_next(command) 
            else:
                    print(f"Unknown topic: {topic} and message: {message}")
        except json.JSONDecodeError:
            print(f"Invalid JSON received: {message}")
  

    def emit_command(self, command: dict):  
        print(f"📡 Emitting command: {command}")
        self.ucp_client.publish("ucl/commands/NovaCore", json.dumps(command))

    def emit_intent(self, intent: dict):
        print(f"📡 Emitting intent: {intent}")
        self.ucp_client.publish("ucl/intents/NovaCore", json.dumps(intent))



    # ucp_pubsub.py
    def emit_context(self, context: dict):
        print(f"📡 Emitting context: {context}")
        self.ucp_client.publish("ucl/context/NovaCore", json.dumps(context))

    def emit_response(self, response: dict):
        print(f"📡 Emitting response: {response}")
        self.ucp_client.publish("ucl/responses/NovaCore", json.dumps(response))  

    def emit_state(self, state_update: dict):
        print(f"📡 Emitting state update: {state_update}")
        """Update state only if something changed and publish to UCP for global sync."""
        current_state = self.state_stream.value
        timestamp = datetime.now().isoformat()

        # Only store new values, preventing unnecessary updates
        updated_state = {}
        for key, value in state_update.items():
            if key not in current_state or current_state[key] != value:
                updated_state[key] = {"value": value, "timestamp": timestamp}

        if updated_state:  # Only emit if something actually changed
            self.ucp_client.publish("ucl/state/NovaCore", json.dumps(updated_state))

    
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