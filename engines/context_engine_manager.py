from threading import Lock

class ContextEngineManager:
    def __init__(self):
        self.context = {}
        self.lock = Lock()

    def get_context(self, key):
        with self.lock:
            return self.context.get(key)

    def update_context(self, key, value):
        with self.lock:
            self.context[key] = value
            self.notify_subscribers(key, value)

    def notify_subscribers(self, key, value):
        # Notify subscribed engines about context updates
        print(f"Context updated: {key} -> {value}")

# Usage Example

