from rate_limiter.client_registry import ClientRegistry
from rate_limiter.strategies import RateLimitStrategy, FixedWindowStrategy
from rate_limiter.entities import RateLimitState
from typing import Optional, Dict
import threading


class RateLimiter:
    def __init__(
        self,
        client_registry: ClientRegistry,
        rate_limit_strategy: Optional[RateLimitStrategy],
    ):
        self.client_registry = client_registry
        self.client_states: Dict[str, RateLimitState] = dict()
        self._lock = threading.Lock()
        self.rate_limit_strategy = rate_limit_strategy or FixedWindowStrategy()

        with self._lock:
            for client_id in self.client_registry.clients:
                client = self.client_registry.clients[client_id]
                self.client_states[client_id] = RateLimitState(
                    max_requests=client.config.max_requests,
                    window_seconds=client.config.window_seconds,
                )

    def allow(self, client_id: str, current_time: float) -> bool:
        with self._lock:
            if client_id not in self.client_registry.clients:
                raise KeyError("Client not registered.")

            if client_id not in self.client_states:
                client = self.client_registry.clients[client_id]
                self.client_states[client_id] = RateLimitState(
                    max_requests=client.config.max_requests,
                    window_seconds=client.config.window_seconds,
                )

            client_state = self.client_states[client_id]

            if not self.rate_limit_strategy.is_allowed(client_state, current_time):
                return False

            client_state.add_request(current_time)
            return True
