# Rate Limiter

A thread-safe, extensible rate limiter implementation in Python for learning Low-Level Design (LLD) concepts.

## Core Requirements

The goal was to design a rate limiter with the following requirements:

1. **Request validation** - decide if a client's request should be allowed or rejected
2. **Per-client limits** - each client has independent rate limits
3. **Configurable limits** - support different limits per client (e.g., 5 requests/60 seconds)
4. **Multiple clients** - track state for many clients simultaneously
5. **Thread safety** - handle concurrent requests from same/different clients
6. **Fast lookups** - checking if request is allowed should be O(1) or O(log n)
7. **Extensibility** - support multiple algorithms (Fixed Window, Sliding Window, Token Bucket, etc.)
8. **Memory efficiency** - don't store unnecessary data

## Implementation Approach

Starting from these requirements, the design evolved through:

1. **Core entities identified**: Client, ClientConfig, RateLimitState, RateLimiter, ClientRegistry
2. **Responsibilities defined**:
   - ClientRegistry manages client lifecycle
   - RateLimiter coordinates rate limiting logic
   - RateLimitState tracks request timestamps per client
   - Strategy pattern for different algorithms
3. **Key decisions**:
   - Store only timestamps (not full requests) for memory efficiency
   - Use deque for O(1) cleanup of old timestamps
   - Dependency injection instead of singleton for testability
   - Strategy pattern for extensibility (Fixed/Sliding Window)
   - Per-client configuration via ClientConfig

## Features

- **Multiple rate limiting strategies** - Fixed Window, Sliding Window (extensible to Token Bucket, Leaky Bucket)
- **Per-client configuration** - Each client can have independent rate limits
- **Thread-safe operations** - Concurrent requests handled safely
- **Client registry** - Centralized client management with dependency injection
- **Efficient cleanup** - Automatic removal of expired request timestamps
- **Extensible design** - Easy to add new strategies via Strategy pattern

## Architecture

```
RateLimiter
├── ClientRegistry (manages clients)
├── RateLimitStrategy (Fixed/Sliding Window)
└── RateLimitState (per-client request tracking)
```

## Project Structure

```
rate_limiter/
├── __init__.py
├── entities.py          # Core data structures (Client, ClientConfig, RateLimitState, Request)
├── client_registry.py   # Client management
├── strategies.py        # Rate limiting strategies (Fixed/Sliding Window)
├── rate_limiter.py      # Main RateLimiter class
├── main.py             # Example usage and demo
└── README.md
```

## Core Components

### 1. Client & ClientConfig

```python
from rate_limiter.entities import Client, ClientConfig

# Create client with custom config
client = Client(
    name="APIClient",
    config=ClientConfig(max_requests=100, window_seconds=60)
)

# Create client with defaults (5 requests per 60 seconds)
client = Client(name="DefaultClient")
```

### 2. ClientRegistry

```python
from rate_limiter.client_registry import ClientRegistry

registry = ClientRegistry()
registry.register(client)
registry.get(client.id)
registry.unregister(client)
```

### 3. Rate Limiting Strategies

#### Sliding Window Strategy
- **Most accurate** - Tracks exact request timestamps
- **Prevents bursts** - Enforces limit over rolling time window
- **Auto-cleanup** - Removes expired timestamps
- **Use case**: APIs requiring strict rate limiting

```python
from rate_limiter.strategies import SlidingWindowStrategy

strategy = SlidingWindowStrategy()
```

**How it works:**
1. Maintains deque of request timestamps
2. On each request, removes timestamps older than window
3. Checks if count < max_requests
4. Adds new timestamp if allowed

#### Fixed Window Strategy
- **Simple & efficient** - Resets at window boundaries
- **Allows bursts** - Can get 2x limit at boundary (e.g., 5 at 59s, 5 at 61s)
- **Less memory** - Clears all timestamps on window reset
- **Use case**: Less strict scenarios, better performance

```python
from rate_limiter.strategies import FixedWindowStrategy

strategy = FixedWindowStrategy()
```

**How it works:**
1. Calculates current window: `current_time // window_seconds`
2. If new window, clears all timestamps
3. Checks if count < max_requests in current window

### 4. RateLimiter

```python
from rate_limiter.rate_limiter import RateLimiter

limiter = RateLimiter(
    client_registry=registry,
    rate_limit_strategy=SlidingWindowStrategy()
)

# Check if request is allowed
allowed = limiter.allow(client_id, current_time)
```

## Usage Example

```python
from rate_limiter.entities import Client, ClientConfig
from rate_limiter.client_registry import ClientRegistry
from rate_limiter.strategies import SlidingWindowStrategy
from rate_limiter.rate_limiter import RateLimiter
import time

# Create clients with different limits
fast_client = Client(
    name="Premium",
    config=ClientConfig(max_requests=100, window_seconds=60)
)
slow_client = Client(
    name="Free",
    config=ClientConfig(max_requests=10, window_seconds=60)
)

# Register clients
registry = ClientRegistry()
registry.register(fast_client)
registry.register(slow_client)

# Create rate limiter with sliding window strategy
limiter = RateLimiter(registry, SlidingWindowStrategy())

# Make requests
current_time = time.time()
for i in range(15):
    allowed = limiter.allow(slow_client.id, current_time + i)
    print(f"Request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}")
```

## Running the Demo

```bash
python -m rate_limiter.main
```

**Expected output:**
```
============================================================
Testing Sliding Window Strategy
============================================================

FastClient (10 req/60s):
  Request 1: ALLOWED
  Request 2: ALLOWED
  ...
  Request 10: ALLOWED
  Request 11: BLOCKED
  Request 12: BLOCKED

SlowClient (3 req/60s):
  Request 1: ALLOWED
  Request 2: ALLOWED
  Request 3: ALLOWED
  Request 4: BLOCKED
  Request 5: BLOCKED

============================================================
Testing Fixed Window Strategy
============================================================
...
```

## Design Decisions

### Thread Safety

- **ClientRegistry**: Lock protects client dict operations
- **RateLimiter**: Lock protects client_states dict and strategy execution
- **RateLimitState**: No locks needed - accessed only within RateLimiter's lock

### Strategy Pattern

Allows easy extension with new algorithms:

```python
from rate_limiter.strategies import RateLimitStrategy

class TokenBucketStrategy(RateLimitStrategy):
    def is_allowed(self, state: RateLimitState, current_time: float) -> bool:
        # Implement token bucket logic
        pass
```

### Dependency Injection

- No singletons - testable and flexible
- ClientRegistry injected into RateLimiter
- Easy to mock for testing

### Per-Client Configuration

Each client has independent:
- `max_requests` - Maximum requests allowed
- `window_seconds` - Time window duration
- Can override strategy per client if needed

## Comparison: Fixed vs Sliding Window

| Aspect | Fixed Window | Sliding Window |
|--------|-------------|----------------|
| **Accuracy** | Can allow 2x at boundaries | Exact limit enforcement |
| **Memory** | Lower (clears on reset) | Higher (stores all timestamps) |
| **Performance** | Faster | Slightly slower |
| **Bursts** | Allows at boundaries | Prevents bursts |
| **Use Case** | Less critical APIs | Strict rate limiting |

**Example of boundary issue (Fixed Window):**
- Window: 60 seconds, Limit: 5 requests
- Time 59s: 5 requests ✓
- Time 61s: 5 requests ✓ (new window)
- **Result**: 10 requests in 2 seconds!

**Sliding Window prevents this:**
- Always checks last 60 seconds from current time
- No boundary exploitation possible

## Future Extensions

1. **Token Bucket** - Smooth rate limiting with burst capacity
2. **Leaky Bucket** - Fixed processing rate
3. **Distributed Rate Limiting** - Redis-backed for multi-server
4. **Rate limit headers** - `X-RateLimit-Remaining`, `Retry-After`
5. **Metrics & monitoring** - Track blocked requests, client stats
6. **Persistence** - Save state across restarts

## Learning Objectives

This implementation demonstrates:

- **Design Patterns**: Strategy, Dependency Injection
- **Data Structures**: Deque for efficient timestamp management
- **Concurrency**: Thread-safe operations with locks
- **SOLID Principles**: Single responsibility, Open/closed
- **Extensibility**: Easy to add new strategies
- **Clean Architecture**: Separation of concerns

## License

Educational project for LLD learning purposes.
