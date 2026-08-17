"""
Design a Parking Lot system

Core requirements:
1. The parking lot should have multiple levels, each level with a certain number of parking spots.
2. The parking lot should support different types of vehicles, such as cars, motorcycles, and trucks.
3. Each parking spot should be able to accommodate a specific type of vehicle.
4. The system should assign a parking spot to a vehicle upon entry and release it when the vehicle exits.
5. The system should track the availability of parking spots and provide real-time information to customers.
6. The system should handle multiple entry and exit points and support concurrent access.
"""

import time

from parking_lot.gate import Gate, GateType
from parking_lot.models.parking_floor import ParkingFloor
from parking_lot.parking_lot import ParkingLot
from parking_lot.models.parking_spot import ParkingSpot
from parking_lot.strategies.parking_strategy import BestFitStrategy
from parking_lot.strategies.pricing_strategy import TieredPricingStrategy
from parking_lot.models.vehicle import Motorcycle, Car, Truck

if __name__ == "__main__":
    spots_floor1 = [ParkingSpot(2), ParkingSpot(4), ParkingSpot(4), ParkingSpot(8)]
    spots_floor2 = [ParkingSpot(2), ParkingSpot(2), ParkingSpot(4), ParkingSpot(8)]

    floor1 = ParkingFloor(1, spots_floor1)
    floor2 = ParkingFloor(2, spots_floor2)

    parking_lot = ParkingLot(
        [floor1, floor2], BestFitStrategy(), TieredPricingStrategy()
    )

    entry_gate_1 = Gate("E1", GateType.ENTRY, floor_number=1)
    entry_gate_2 = Gate("E2", GateType.ENTRY, floor_number=2)
    exit_gate_1 = Gate("X1", GateType.EXIT, floor_number=1)
    exit_gate_2 = Gate("X2", GateType.EXIT, floor_number=2)

    motorcycle = Motorcycle("MC-1234")
    car = Car("CAR-5678")
    truck = Truck("TRK-9012")

    print("=" * 60)
    print("PARKING LOT SYSTEM - ENTRY PHASE")
    print("=" * 60)

    ticket1 = entry_gate_1.process_entry(motorcycle, parking_lot)
    print(f"Assigned spot: {ticket1.spot.name}\n")

    ticket2 = entry_gate_2.process_entry(car, parking_lot)
    print(f"Assigned spot: {ticket2.spot.name}\n")

    ticket3 = entry_gate_1.process_entry(truck, parking_lot)
    print(f"Assigned spot: {ticket3.spot.name}\n")

    print(f"Active tickets: {len(parking_lot.active_tickets)}")

    print("\n" + "=" * 60)
    print("PARKING LOT SYSTEM - EXIT PHASE")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("ERROR HANDLING TESTS")
    print("=" * 60)

    try:
        print("\nAttempting to enter already parked vehicle...")
        entry_gate_1.process_entry(motorcycle, parking_lot)
    except ValueError as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("PARKING LOT SYSTEM - EXIT PHASE")
    print("=" * 60)

    time.sleep(2)
    fee2 = exit_gate_2.process_exit(ticket2, parking_lot)
    print(f"Duration: {ticket2.get_duration_hours()} hour(s)\n")

    print(f"Active tickets: {len(parking_lot.active_tickets)}\n")

    time.sleep(3)
    fee1 = exit_gate_1.process_exit(ticket1, parking_lot)
    print(f"Duration: {ticket1.get_duration_hours()} hour(s)\n")

    time.sleep(1)
    fee3 = exit_gate_1.process_exit(ticket3, parking_lot)
    print(f"Duration: {ticket3.get_duration_hours()} hour(s)\n")

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total vehicles processed: 3")
    print(f"Total revenue: ${fee1 + fee2 + fee3:.2f}")
    print(f"Active tickets: {len(parking_lot.active_tickets)}")

    print("\n" + "=" * 60)
    print("MORE ERROR TESTS")
    print("=" * 60)

    try:
        print("\nAttempting to exit with already used ticket...")
        exit_gate_1.process_exit(ticket2, parking_lot)
    except ValueError as e:
        print(f"Error: {e}")

    try:
        print("\nAttempting to exit from entry gate...")
        entry_gate_1.process_exit(ticket1, parking_lot)
    except ValueError as e:
        print(f"Error: {e}")
