from abc import ABC, abstractmethod
from parking_lot.models.vehicle import Vehicle, Motorcycle, Car, Truck


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, duration_hours: float, vehicle: Vehicle) -> float:
        pass


class TieredPricingStrategy(PricingStrategy):
    def __init__(self):
        self.rates = {Motorcycle: 2.0, Car: 5.0, Truck: 10.0}

    def calculate_fee(self, duration_hours: float, vehicle: Vehicle) -> float:
        rate = self.rates.get(type(vehicle), 5.0)
        return duration_hours * rate
