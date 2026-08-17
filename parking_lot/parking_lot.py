from typing import List
from parking_lot.models.parking_floor import ParkingFloor
from parking_lot.strategies.parking_strategy import ParkingStrategy
from parking_lot.models.parking_ticket import ParkingTicket
from parking_lot.strategies.pricing_strategy import PricingStrategy
from parking_lot.models.parking_ticket import ParkingState
import threading
import time


class ParkingLot:
    def __init__(
        self,
        parking_floors: List[ParkingFloor],
        parking_strategy: ParkingStrategy,
        pricing_strategy: PricingStrategy,
    ):
        self.floors = parking_floors
        self.parking_strategy = parking_strategy
        self.pricing_strategy = pricing_strategy
        self.active_tickets: dict[str, ParkingTicket] = {}
        self._lock = threading.Lock()

    def find_available_spots(self, vehicle):
        available_spots = set()
        for floor in self.floors:
            available_spots.update(floor.find_spots(vehicle))

        return available_spots

    def park_vehicle(self, vehicle: Vehicle):
        with self._lock:
            if vehicle.id in self.active_tickets:
                raise ValueError(f"Vehicle {vehicle.license_number} is already parked")

        available_spots = self.find_available_spots(vehicle)
        if not available_spots:
            raise Exception(f"No available spots for {vehicle.name}")

        while available_spots:
            spot = self.parking_strategy.choose_spot(available_spots, vehicle)
            response = spot.park_vehicle(vehicle)
            if response:
                current_time = time.time()
                parking_ticket = ParkingTicket(spot, vehicle, current_time)
                with self._lock:
                    self.active_tickets[vehicle.id] = parking_ticket
                return parking_ticket
            available_spots.discard(spot)

        raise Exception(f"Failed to park {vehicle.name}")

    def unpark_vehicle(self, parking_ticket):
        with self._lock:
            if parking_ticket.vehicle.id not in self.active_tickets:
                raise ValueError("Invalid or already used ticket")

            stored_ticket = self.active_tickets[parking_ticket.vehicle.id]
            if stored_ticket.id != parking_ticket.id:
                raise ValueError("Ticket mismatch")

            if parking_ticket.state != ParkingState.ACTIVE:
                raise ValueError("Ticket is not active")

        spot = parking_ticket.spot
        current_time = time.time()
        spot.unpark_vehicle(parking_ticket.vehicle)
        parking_ticket.discard(current_time)

        duration_hours = parking_ticket.get_duration_hours()
        fee = self.pricing_strategy.calculate_fee(
            duration_hours, parking_ticket.vehicle
        )
        parking_ticket.fee = fee

        with self._lock:
            del self.active_tickets[parking_ticket.vehicle.id]

        return fee
