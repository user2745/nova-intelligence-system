# ucp_pubsub.py  
from rx.subject import Subject, BehaviorSubject  
from ucp import UCPClient, UCPServer
from datetime import datetime
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


        self.state_stream = BehaviorSubject({});

        self.response_stream = Subject()
        self.transaction_stream = Subject()

        # External UCPClient for Flutter communication
        self.ucp_client = UCPClient(device_id="NovaCore", broker_address="100.115.157.25")
        self.ucp_client.connect()
        self.ucp_client.subscribe("ucl/commands/NovaCore")

        # Connection to the UCPClient for distributed state

        self.ucp_client.subscribe("ucl/state/NovaCore");

        # Forward commands from UCPClient to internal streams
        self.ucp_client.set_message_handler(self._handle_incoming_message)

        # Forward responses from internal streams to UCPClient
        self.response_stream.subscribe(
            lambda resp: self.ucp_client.publish("ucl/responses/NovaCore", resp)
        )

        # Forward context from internal streams to UCPClient
        self.state_stream.subscribe(
            lambda state: self.ucp_client.publish("ucl/state/NovaCore", json.dumps(state))
        )

        # Start heartbeat
        self.ucp_client.start_heartbeat(interval=10)

    def _handle_incoming_message(self, topic, message):
        try:
            command = json.loads(message)
            if topic == "ucl/state/NovaCore":
                self._merge_state(command)
            else:
                self.command_stream.on_next(command)
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
        """Update and propagate state"""
        current_state = self.state_stream.value
        merged_state = {**current_state, **state_update}  # Merge changes
        self.state_stream.on_next(merged_state)

    def _merge_state(self, incoming_state):
        """Merge incoming state updates from other Nova instances"""
        current_state = self.state_stream.value
        merged_state = {**current_state, **incoming_state}  # Merge dictionaries
        self.state_stream.on_next(merged_state)  # Apply merged state