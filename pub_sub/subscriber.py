from abc import ABC, abstractmethod
from pub_sub.entities import DeliveryContext
from uuid import uuid4


class Subscriber(ABC):
    def __init__(self, name=None):
        self.id = str(uuid4())
        self.name = name or f"Subscriber-{self.id[:8]}"

    @abstractmethod
    def on_message(self, delivery: DeliveryContext):
        pass

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Subscriber):
            return False
        return self.id == other.id
