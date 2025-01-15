from threading import Lock

class MutableContext:
    def __init__(self, immutable_context, redis_connector):
        self._context = {}
        self.lock = Lock()
        self.immutable_context = immutable_context
        self.redis = redis_connector
        self.subscribers = []

    def get_current_context(self):
        """
        Get the current mutable context.
        """
        with self.lock:
            return self._context

    def get_context(self, key):
        with self.lock:
            return self._context.get(key)

    def update_context(self, key, value):
        """
        Update the mutable context and notify subscribers.
        """
        with self.lock:
            self._context[key] = value
            self.redis.save_context_snapshot(key, value)
        print(f"Mutable context updated: {key} -> {value}")
        self.notify_subscribers(key, value)

    def restore_context(self, key):
        """
        Restore a context value from QuestDB.
        """
        with self.lock:
            value = self.redis.load_context_snapshot(key)
            if value:
                self._context[key] = value
                print(f"Context restored from QuestDB: {key} -> {value}")
            return value

    def subscribe(self, callback=None):
        """
        Subscribe a component to context updates.
        """
        if callback:
            self.subscribers.append(callback)

    def notify_subscribers(self, key, value):
        """
        Notify all subscribers of a context update.
        """
        for subscriber in self.subscribers:
            try:
                subscriber(key, value)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")

    def freeze(self):
        """
        Propagate the current mutable context to the immutable pool.
        """
        with self.lock:
            self.immutable_context.snapshot(self._context)
        print("Mutable context frozen.")
