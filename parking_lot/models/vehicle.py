from abc import ABC
from uuid import uuid4


class Vehicle(ABC):
    pass


class Motorcycle(Vehicle):
    def __init__(self, license_number):
        self.id = str(uuid4())
        self.license_number = license_number
        self.area = 2


class Car(Vehicle):
    def __init__(self, license_number):
        self.id = str(uuid4())
        self.license_number = license_number
        self.area = 4


class Truck(Vehicle):
    def __init__(self, license_number):
        self.id = str(uuid4())
        self.license_number = license_number
        self.area = 8
