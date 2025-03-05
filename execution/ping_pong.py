from rx import operators as ops

class PingPong:
    def __init__(self, ucp):
        self.ucp = ucp
        ucp.command_stream.pipe(
            ops.filter(lambda cmd: cmd.get("action") == "ping"),
        ).subscribe(self._handle_ping)

    def _handle_ping(self, data):
        try:
            print(f"🏓 Received ping: {data}")
            self.ucp.emit_response({"type": "pong"})
        except Exception as e:
            print(f"Error handling ping: {str(e)}")
            self.ucp.emit_response({"type": "pong", "error": str(e)})