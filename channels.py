import socket
from rx.subject import Subject, BehaviorSubject  
from ucp import UCPClient, UCPServer
from datetime import datetime
import asyncio
import os
import json


class Channels:
    def __init__(self):
        hostname = socket.gethostname()
        self.client = UCPClient(device_id=f"NovaCore-{hostname}", broker_address="localhost")

        self.client.connect()
        self.client.set_message_handler(self._on_message)
        # Start heartbeat
        self.client.start_heartbeat(interval=10)


    def emit(self, channel, data):
        self.client.publish(f"channel/{channel}/internal", data)

    def consume(self, channel):
        self.client.subscribe(f"channel/{channel}/internal", self._on_message)

    def subscribe(self, fn):
        lambda resp: self.client.publish("channel/sync/internal", json.dumps(resp))

    def syncwithPeers(self, data):
        # Sync with other gundb peers
        self.client.publish("channel/sync/", data)
        # gundb connection
        

    def _on_message(self, message):
        # Handle incoming messages
        print(f"Received message on channel: {message['channel']}")
        pass
    
