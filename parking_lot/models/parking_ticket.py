from enum import Enum
from uuid import uuid4
import math


class ParkingState(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class ParkingTicket:
    def __init__(self, parking_spot, vehicle, current_time):
        self.id = str(uuid4())
        self.entry_time: float = current_time
        self.spot: ParkingSpot = parking_spot
        self.vehicle: Vehicle = vehicle
        self.state = ParkingState.ACTIVE
        self.exit_time = None
        self.fee = 0.0

    def discard(self, current_time):
        self.exit_time = current_time
        self.state = ParkingState.COMPLETED

    def get_duration_hours(self):
        if self.exit_time is None:
            raise ValueError("Vehicle not yet exited")
        duration_seconds = self.exit_time - self.entry_time
        duration_hours = duration_seconds / 3600
        return math.ceil(duration_hours)
