"""Async token-bucket rate limiter (Alpaca free plan: 200 requests/minute)."""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    def __init__(self, per_minute: int, *, clock=time.monotonic) -> None:  # noqa: ANN001
        if per_minute <= 0:
            raise ValueError("per_minute must be positive")
        self.capacity = float(per_minute)
        self.rate = per_minute / 60.0  # tokens per second
        self._tokens = self.capacity
        self._clock = clock
        self._last = clock()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = self._clock()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
        self._last = now

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                await asyncio.sleep((1 - self._tokens) / self.rate)

    def drain(self) -> None:
        """Called after a 429 so we back off even if our own count disagrees with the server's."""
        self._tokens = 0
        self._last = self._clock()
