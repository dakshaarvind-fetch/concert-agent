"""Token-bucket rate limiter for Ticketmaster (5 req/s) — step 4."""
import asyncio
import time


class TokenBucket:
    """Async token bucket. Thread-safe via asyncio.Lock."""

    def __init__(self, rate: float, capacity: float) -> None:
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(
                self._capacity,
                self._tokens + elapsed * self._rate,
            )
            self._last_refill = now
            if self._tokens < 1:
                wait = (1 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0
            else:
                self._tokens -= 1


# Singleton for Ticketmaster (5 req/s, burst up to 5)
ticketmaster_bucket = TokenBucket(rate=5.0, capacity=5.0)
