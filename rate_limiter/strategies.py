from abc import ABC, abstractmethod
from rate_limiter.entities import RateLimitState


class RateLimitStrategy(ABC):
    @abstractmethod
    def is_allowed(self, state: RateLimitState, current_time: float) -> bool:
        pass


class FixedWindowStrategy(RateLimitStrategy):
    def is_allowed(self, state: RateLimitState, current_time: float) -> bool:
        current_window = int(current_time // state.window_seconds)

        if not state.timestamps:
            return True

        first_request_window = int(state.timestamps[0] // state.window_seconds)

        if current_window != first_request_window:
            state.timestamps.clear()
            return True

        return state.count_requests() < state.max_requests


class SlidingWindowStrategy(RateLimitStrategy):
    def is_allowed(self, state: RateLimitState, current_time: float) -> bool:
        state.cleanup(current_time)
        return state.count_requests() < state.max_requests
