"""Tests for RateLimiter."""

from __future__ import annotations

import pytest

from boostylib.http.rate_limiter import RateLimiter

pytestmark = pytest.mark.unit


class TestRateLimiter:
    async def test_acquire_within_limit(self) -> None:
        limiter = RateLimiter(max_requests=10, period=1.0)
        for _ in range(10):
            await limiter.acquire()

    async def test_tokens_decrease(self) -> None:
        limiter = RateLimiter(max_requests=5, period=60.0)
        await limiter.acquire()
        assert limiter._tokens < 5.0
