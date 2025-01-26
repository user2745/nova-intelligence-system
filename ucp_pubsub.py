# ucp_pubsub.py  
from rx.subject import Subject, BehaviorSubject  
from ucp import UCPClient, UCPServer
import json

class UCPPubSub:  
    def __init__(self):  
        # Internal RxPy streams
        self.command_stream = Subject()
        self.context_stream = BehaviorSubject({"status": "booting"})
        self.response_stream = Subject()
        self.transaction_stream = Subject()

        # External UCPClient for Flutter communication
        self.ucp_client = UCPClient(device_id="NovaCore", broker_address="100.115.157.25")
        self.ucp_client.connect()
        self.ucp_client.subscribe("ucl/commands/NovaCore")

        # Forward commands from UCPClient to internal streams
        self.ucp_client.set_message_handler(self._handle_incoming_message)

        # Forward responses from internal streams to UCPClient
        self.response_stream.subscribe(
            lambda resp: self.ucp_client.publish("ucl/responses/NovaCore", resp)
        )

        # Start heartbeat
        self.ucp_client.start_heartbeat(interval=10)

    def _handle_incoming_message(self, topic, message):
        try:
            command = json.loads(message)
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