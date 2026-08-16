from rate_limiter.entities import Client
from typing import Dict
import threading


class ClientRegistry:
    def __init__(self):
        self.clients: Dict[str, Client] = dict()
        self._lock = threading.Lock()

    def register(self, client: Client):
        with self._lock:
            if client.id in self.clients:
                return
            self.clients[client.id] = client

    def unregister(self, client):
        with self._lock:
            if client.id not in self.clients:
                return
            del self.clients[client.id]

    def get(self, client_id: str):
        with self._lock:
            if client_id not in self.clients:
                raise KeyError("Client not present in Registry.")
            return self.clients[client_id]
