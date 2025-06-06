class BaseCodelet(threading.Thread):
    def __init__(self, name: str, inbox: queue.Queue, outbox: queue.Queue):
        super().__init__(daemon=True)
        self.name, self.inbox, self.outbox = name, inbox, outbox
        self.running = True

    def run(self):
        while self.running:
            try:
                item = self.inbox.get(timeout=0.1)
                self.process(item)
            except queue.Empty:
                continue                      # wake up later

    def process(self, item):
        """Override in subclass."""
        pass

    def stop(self):
        self.running = False