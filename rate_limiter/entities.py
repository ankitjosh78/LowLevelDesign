from dataclasses import dataclass
from collections import deque
from typing import Any, Optional
from uuid import uuid4


@dataclass
class Request:
    request_id: str
    payload: Any
    timestamp: float


@dataclass
class ClientConfig:
    max_requests: int = 5
    window_seconds: int = 60


class RateLimitState:
    def __init__(self, max_requests=5, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: deque[float] = deque()

    def add_request(self, current_timestamp):
        self.timestamps.append(current_timestamp)

    def cleanup(self, current_timestamp):
        cutoff = current_timestamp - self.window_seconds
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()

    def count_requests(self):
        return len(self.timestamps)


class Client:
    def __init__(
        self, name=None, ip_address=None, config: Optional[ClientConfig] = None
    ):
        self.id = str(uuid4())
        self.name = name or f"Client-{self.id[:8]}"
        self.ip_address = ip_address or "127.0.0.1"
        self.config = config or ClientConfig()
