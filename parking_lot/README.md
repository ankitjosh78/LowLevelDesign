# Parking Lot System

A multi-level parking lot management system with entry/exit gates, multiple vehicle types, and dynamic pricing strategies.

## Core Requirements

The goal was to design a parking lot system with the following requirements:

1. **Multiple levels** - Support multiple floors with varying numbers of parking spots
2. **Vehicle types** - Handle different vehicles (motorcycles, cars, trucks)
3. **Spot compatibility** - Each spot accommodates specific vehicle sizes
4. **Entry/Exit management** - Assign spots on entry, release on exit
5. **Real-time tracking** - Track availability and occupancy
6. **Multiple gates** - Support concurrent entry/exit points
7. **Thread safety** - Handle concurrent access safely
8. **Pricing system** - Calculate fees based on duration and vehicle type

## Implementation Approach

Starting from these requirements, the design evolved through:

1. **Core entities identified**: Vehicle, ParkingSpot, ParkingFloor, ParkingTicket, Gate, ParkingLot
2. **Responsibilities defined**:
   - Gate handles entry/exit operations
   - ParkingLot coordinates parking logic and ticket management
   - ParkingFloor manages spots on each level
   - ParkingSpot handles individual spot state
   - Strategies determine spot selection and pricing
3. **Key decisions**:
   - Strategy pattern for parking algorithms (BestFit, Nearest, Largest)
   - Strategy pattern for pricing (Tiered by vehicle type)
   - Thread-safe ticket registry to prevent double parking/exit
   - License plate-based vehicle identification
   - Modular package structure for maintainability

## Project Structure

```
parking_lot/
├── models/                    # Domain entities
│   ├── vehicle.py            # Vehicle, Motorcycle, Car, Truck
│   ├── parking_spot.py       # ParkingSpot with thread-safe operations
│   ├── parking_floor.py      # ParkingFloor managing multiple spots
│   └── parking_ticket.py     # ParkingTicket, ParkingState
├── strategies/               # Strategy pattern implementations
│   ├── parking_strategy.py   # NearestSpot, BestFit, LargestSpot
│   └── pricing_strategy.py   # TieredPricing
├── parking_lot.py            # Core ParkingLot orchestration
├── gate.py                   # Gate, GateType (ENTRY/EXIT)
├── main.py                   # Demo
└── README.md
```

## Features

- **Multiple parking strategies** - BestFit (smallest suitable), Nearest, Largest
- **Tiered pricing** - Different rates per vehicle type (Motorcycle: $2/hr, Car: $5/hr, Truck: $10/hr)
- **Entry/Exit gates** - Multiple gates on different floors
- **Thread-safe operations** - Concurrent parking/unparking handled safely
- **Ticket validation** - Prevents double parking, invalid exits, ticket fraud
- **Duration tracking** - Automatic fee calculation based on parking time
- **Real-time availability** - Track active tickets and occupancy

## Usage

### Basic Flow

```python
from parking_lot.models.vehicle import Motorcycle, Car, Truck
from parking_lot.models.parking_spot import ParkingSpot
from parking_lot.models.parking_floor import ParkingFloor
from parking_lot.parking_lot import ParkingLot
from parking_lot.gate import Gate, GateType
from parking_lot.strategies.parking_strategy import BestFitStrategy
from parking_lot.strategies.pricing_strategy import TieredPricingStrategy

# Setup parking lot
spots_floor1 = [ParkingSpot(2), ParkingSpot(4), ParkingSpot(8)]
floor1 = ParkingFloor(1, spots_floor1)

parking_lot = ParkingLot(
    [floor1], 
    BestFitStrategy(), 
    TieredPricingStrategy()
)

# Create gates
entry_gate = Gate("E1", GateType.ENTRY, floor_number=1)
exit_gate = Gate("X1", GateType.EXIT, floor_number=1)

# Entry
car = Car("ABC-1234")
ticket = entry_gate.process_entry(car, parking_lot)

# Exit
fee = exit_gate.process_exit(ticket, parking_lot)
print(f"Fee: ${fee:.2f}")
```

## Running the Demo

```bash
python -m parking_lot.main
```

**Output:**
```
============================================================
PARKING LOT SYSTEM - ENTRY PHASE
============================================================
[Gate E1 - Floor 1] Vehicle MC-1234 entering...
[Gate E1] Ticket issued: 7e7025c7
Assigned spot: ParkingSpot-id-30063902

...

============================================================
SUMMARY
============================================================
Total vehicles processed: 3
Total revenue: $17.00
Active tickets: 0
```

## Design Patterns Used

### 1. Strategy Pattern (Parking Spot Selection)

```python
class ParkingStrategy(ABC):
    @abstractmethod
    def choose_spot(self, spots: Set[ParkingSpot], vehicle: Vehicle) -> ParkingSpot:
        pass

class BestFitStrategy(ParkingStrategy):
    def choose_spot(self, spots, vehicle):
        return min(spots, key=lambda spot: spot.area)
```

**Benefit**: Easy to add new strategies (e.g., FloorPreference, HandicappedPriority)

### 2. Strategy Pattern (Pricing)

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, duration_hours: float, vehicle: Vehicle) -> float:
        pass

class TieredPricingStrategy(PricingStrategy):
    def calculate_fee(self, duration_hours, vehicle):
        rate = self.rates.get(type(vehicle), 5.0)
        return duration_hours * rate
```

**Benefit**: Support different pricing models (hourly, daily cap, time-slab)

### 3. Dependency Injection

```python
class ParkingLot:
    def __init__(self, floors, parking_strategy, pricing_strategy):
        self.parking_strategy = parking_strategy
        self.pricing_strategy = pricing_strategy
```

**Benefit**: Testable, flexible, no global state

## Key Design Decisions

### Thread Safety

- **ParkingSpot**: Lock per spot for park/unpark operations
- **ParkingLot**: Lock for ticket registry operations
- **Validation**: Check-then-act protected by locks

### Ticket Validation

```python
def unpark_vehicle(self, parking_ticket):
    with self._lock:
        # Validate ticket exists
        if parking_ticket.vehicle.id not in self.active_tickets:
            raise ValueError("Invalid or already used ticket")
        
        # Validate ticket ID matches
        stored_ticket = self.active_tickets[parking_ticket.vehicle.id]
        if stored_ticket.id != parking_ticket.id:
            raise ValueError("Ticket mismatch")
```

Prevents:
- Double exit with same ticket
- Fake ticket creation
- Ticket reuse

### Spot Size vs Vehicle Area

Current implementation uses numeric `area` (2, 4, 8). Could be improved with:

```python
class SpotType(Enum):
    COMPACT = "compact"
    REGULAR = "regular"
    LARGE = "large"

class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"
```

### Duration Calculation

```python
def get_duration_hours(self):
    duration_seconds = self.exit_time - self.entry_time
    duration_hours = duration_seconds / 3600
    return math.ceil(duration_hours)  # Round up to nearest hour
```

Standard practice: Even 1 minute = 1 hour charge

## Error Handling

The system validates:

1. **Double parking** - Vehicle already has active ticket
2. **Invalid ticket** - Ticket not in active registry
3. **Ticket mismatch** - Ticket ID doesn't match stored ticket
4. **Wrong gate type** - Entry gate used for exit (or vice versa)
5. **No available spots** - Parking lot full for vehicle type

## Future Enhancements

- [ ] **Display boards** - Show available spots per floor/type
- [ ] **Reservation system** - Pre-book spots
- [ ] **Payment integration** - Process actual payments
- [ ] **Admin panel** - Add/remove spots, view analytics
- [ ] **Vehicle search** - Find where a vehicle is parked by license plate
- [ ] **Handicapped spots** - Priority parking with special validation
- [ ] **Electric vehicle charging** - Track charging spots and time
- [ ] **Monthly passes** - Subscription-based parking
- [ ] **Grace period** - First 15 minutes free
- [ ] **Daily cap** - Maximum charge per day

## Learning Objectives

This implementation demonstrates:

- **SOLID Principles** - Single responsibility, Open/closed, Dependency inversion
- **Design Patterns** - Strategy, Dependency Injection
- **Concurrency** - Thread-safe operations with locks
- **Domain Modeling** - Clear entity relationships
- **Error Handling** - Validation and edge cases
- **Clean Architecture** - Separation of concerns, modular structure

## License

Educational project for LLD learning purposes.
