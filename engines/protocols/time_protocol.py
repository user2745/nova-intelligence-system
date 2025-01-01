# protocols/time_protocol.py
from datetime import datetime

def fetch_time():
    now = datetime.now()
    return {
        "datetime": now,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": now.strftime("%A"),
    }
