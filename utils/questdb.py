import psycopg2
from datetime import datetime

class QuestDBConnector:
    def __init__(self, host="localhost", port=8812, user="admin", password="quest"):
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="qdb"
        )
        self.cursor = self.connection.cursor()

    def save_context_snapshot(self, key, value):
        query = """
        INSERT INTO context_snapshots (timestamp, key, value)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (datetime.utcnow(), key, str(value)))
        self.connection.commit()

    def load_context_snapshot(self, key):
        query = "SELECT value FROM context_snapshots WHERE key = %s ORDER BY timestamp DESC LIMIT 1"
        self.cursor.execute(query, (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.cursor.close()
        self.connection.close()
