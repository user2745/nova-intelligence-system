from redis import Redis
import json
from datetime import datetime

class RedisConnector:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = Redis(host=host, port=port, db=db)

    def save_context_snapshot(self, key, value):
        """
        Save a context snapshot with a timestamp to Redis.
        Mimics the behavior of inserting into QuestDB.
        """
        timestamp = datetime.utcnow().isoformat()
        data = {"timestamp": timestamp, "key": key, "value": value}
        self.client.hset("context_snapshots", key, json.dumps(data))

    def load_context_snapshot(self, key):
        """
        Load the latest context snapshot for a key from Redis.
        """
        data = self.client.hget("context_snapshots", key)
        if data:
            snapshot = json.loads(data)
            return snapshot["value"]
        return None

    def close(self):
        """
        Close the Redis connection (no-op as Redis handles this internally).
        """
        pass
