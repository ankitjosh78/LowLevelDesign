from parking_lot.models.parking_spot import ParkingSpot
from typing import List


class ParkingFloor:
    def __init__(self, floor_number, parking_spots: List[ParkingSpot]):
        self.floor_no = floor_number
        self.spots = parking_spots

    def find_spots(self, vehicle):
        available_spots = []
        for spot in self.spots:
            if spot.can_park(vehicle):
                available_spots.append(spot)

        return available_spots
