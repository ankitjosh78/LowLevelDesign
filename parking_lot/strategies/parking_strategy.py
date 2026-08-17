from abc import ABC, abstractmethod
from typing import Set
from parking_lot.models.parking_spot import ParkingSpot
from parking_lot.models.vehicle import Vehicle


class ParkingStrategy(ABC):
    @abstractmethod
    def choose_spot(self, spots: Set[ParkingSpot], vehicle: Vehicle) -> ParkingSpot:
        pass


class NearestSpotStrategy(ParkingStrategy):
    def choose_spot(self, spots: Set[ParkingSpot], vehicle: Vehicle) -> ParkingSpot:
        return next(iter(spots))


class BestFitStrategy(ParkingStrategy):
    def choose_spot(self, spots: Set[ParkingSpot], vehicle: Vehicle) -> ParkingSpot:
        return min(spots, key=lambda spot: spot.area)


class LargestSpotStrategy(ParkingStrategy):
    def choose_spot(self, spots: Set[ParkingSpot], vehicle: Vehicle) -> ParkingSpot:
        return max(spots, key=lambda spot: spot.area)
