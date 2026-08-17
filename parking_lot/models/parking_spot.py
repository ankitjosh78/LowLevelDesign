from uuid import uuid4
import threading


class ParkingSpot:
    # Let's have a caveat, that we can only park one vehicle at a parking spot. Regardless if it's big or small
    def __init__(self, spot_area):
        self.id = str(uuid4())
        self.name = f"ParkingSpot-id-{self.id[:8]}"
        self.area = spot_area
        self.is_occupied = False
        self.parked_vehicle = None
        self._lock = threading.Lock()

    def can_park(self, vehicle):
        with self._lock:
            return not self.is_occupied and vehicle.area <= self.area

    def park_vehicle(self, vehicle):
        with self._lock:
            if not self.is_occupied and vehicle.area <= self.area:
                self.is_occupied = True
                self.parked_vehicle = vehicle
                return True
            return False

    def unpark_vehicle(self, vehicle):
        with self._lock:
            if self.parked_vehicle == vehicle:
                self.parked_vehicle = None
                self.is_occupied = False
