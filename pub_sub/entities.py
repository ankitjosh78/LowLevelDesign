from dataclasses import dataclass
from typing import Any
from uuid import uuid4
from enum import Enum


@dataclass
class Message:
    message_id: str
    payload: Any


class DeliveryStatus(Enum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FAILED = "FAILED"
    PENDING = "PENDING"


class DeliveryContext:
    def __init__(self, message: Message, max_attempts=3):
        self.delivery_id = str(uuid4())
        self.attempt = 1
        self.max_attempts = max_attempts
        self.status = DeliveryStatus.PENDING
        self.message = message
        self.error = None

    def acknowledge(self):
        self.status = DeliveryStatus.ACKNOWLEDGED

    def fail(self, error=None):
        self.status = DeliveryStatus.FAILED
        self.error = error

    def increment_attempt(self):
        self.attempt += 1
