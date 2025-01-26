# ucp_pubsub.py
from rx.subject import Subject
from rx.subject import BehaviorSubject  # <-- Change from Subject

class UCPPubSub:
    def __init__(self):
        # Core streams (our "streets")
        self.command_stream = Subject()  # Raw commands from users/LLMs
        self.transaction_stream = Subject()  # Blockchain ops
        self.context_stream = BehaviorSubject({"status": "booting"})  # Initial context
        self.response_stream = Subject()  # Outcomes to send back

    def emit_command(self, command: dict):
        """Throw a command into the streets."""
        self.command_stream.on_next(command)

    def emit_context(self, context: dict):
        """Broadcast a context update."""
        self.context_stream.on_next(context)

    def emit_response(self, response: dict):
        """Shout a response to the world."""
        self.response_stream.on_next(response)