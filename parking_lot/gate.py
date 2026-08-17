from enum import Enum
from parking_lot.models.parking_ticket import ParkingTicket
from parking_lot.parking_lot import ParkingLot
from parking_lot.models.vehicle import Vehicle


class GateType(Enum):
    ENTRY = "entry"
    EXIT = "exit"


class Gate:
    def __init__(self, gate_id: str, gate_type: GateType, floor_number: int):
        self.id = gate_id
        self.type = gate_type
        self.floor_number = floor_number

    def process_entry(self, vehicle: Vehicle, parking_lot: ParkingLot) -> ParkingTicket:
        if self.type != GateType.ENTRY:
            raise ValueError(f"Gate {self.id} is not an entry gate")

        print(
            f"[Gate {self.id} - Floor {self.floor_number}] Vehicle {vehicle.license_number} entering..."
        )
        ticket = parking_lot.park_vehicle(vehicle)
        print(f"[Gate {self.id}] Ticket issued: {ticket.id[:8]}")
        return ticket

    def process_exit(
        self, parking_ticket: ParkingTicket, parking_lot: ParkingLot
    ) -> float:
        if self.type != GateType.EXIT:
            raise ValueError(f"Gate {self.id} is not an exit gate")

        print(
            f"[Gate {self.id} - Floor {self.floor_number}] Vehicle {parking_ticket.vehicle.license_number} exiting..."
        )
        fee = parking_lot.unpark_vehicle(parking_ticket)
        print(f"[Gate {self.id}] Fee collected: ${fee:.2f}")
        return fee
