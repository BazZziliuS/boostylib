"""Token-bucket rate limiter for API requests."""

from __future__ import annotations

import asyncio
import logging
import time

logger = logging.getLogger("boostylib.rate_limiter")


class RateLimiter:
    """Token-bucket rate limiter.

    Args:
        max_requests: Maximum number of requests allowed in the period.
        period: Time period in seconds for the rate limit window.
    """

    def __init__(self, *, max_requests: int = 60, period: float = 60.0) -> None:
        self.max_requests = max_requests
        self.period = period
        self._tokens = float(max_requests)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            self.max_requests,
            self._tokens + elapsed * (self.max_requests / self.period),
        )
        self._last_refill = now

    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            self._refill()
            if self._tokens < 1.0:
                wait_time = (1.0 - self._tokens) * (self.period / self.max_requests)
                logger.debug("Rate limit: waiting %.2fs", wait_time)
                await asyncio.sleep(wait_time)
                self._refill()
            self._tokens -= 1.0
