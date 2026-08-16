"""
Rate Limiter Demo

Demonstrates different rate limiting strategies with multiple clients.
See README.md for detailed documentation.
"""

from rate_limiter.entities import Client
from rate_limiter.entities import ClientConfig
from rate_limiter.client_registry import ClientRegistry
from rate_limiter.strategies import SlidingWindowStrategy, FixedWindowStrategy
from rate_limiter.rate_limiter import RateLimiter

client1 = Client(
    name="FastClient", config=ClientConfig(max_requests=10, window_seconds=60)
)
client2 = Client(
    name="SlowClient", config=ClientConfig(max_requests=3, window_seconds=60)
)
client3 = Client(name="DefaultClient")

client_registry = ClientRegistry()
client_registry.register(client1)
client_registry.register(client2)
client_registry.register(client3)

rate_limiter = RateLimiter(client_registry, SlidingWindowStrategy())

if __name__ == "__main__":
    import time

    print("=" * 60)
    print("Testing Sliding Window Strategy")
    print("=" * 60)

    current_time = time.time()

    print(f"\nFastClient (10 req/60s):")
    for i in range(12):
        allowed = rate_limiter.allow(client1.id, current_time + i)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}")

    print(f"\nSlowClient (3 req/60s):")
    for i in range(5):
        allowed = rate_limiter.allow(client2.id, current_time + i)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}")

    print(f"\nDefaultClient (5 req/60s):")
    for i in range(7):
        allowed = rate_limiter.allow(client3.id, current_time + i)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}")

    print("\n" + "=" * 60)
    print("Testing Fixed Window Strategy")
    print("=" * 60)

    fixed_limiter = RateLimiter(client_registry, FixedWindowStrategy())

    print(f"\nSlowClient (3 req/60s) - Same window:")
    for i in range(5):
        allowed = fixed_limiter.allow(client2.id, current_time + i)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}")

    print(f"\nSlowClient - After window reset (61s later):")
    for i in range(5):
        allowed = fixed_limiter.allow(client2.id, current_time + 61 + i)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"  Request {i+1}: {status}")
