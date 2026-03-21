"""Tests for RetryPolicy."""

from __future__ import annotations

import pytest

from boostylib.http.exceptions import BoostyRateLimitError, BoostyServerError
from boostylib.http.retry import RetryPolicy

pytestmark = pytest.mark.unit


class TestRetryPolicy:
    def test_should_retry_on_500(self) -> None:
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(500, 0) is True
        assert policy.should_retry(500, 2) is True
        assert policy.should_retry(500, 3) is False

    def test_should_not_retry_on_400(self) -> None:
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(400, 0) is False

    def test_should_retry_on_429(self) -> None:
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(429, 0) is True

    def test_backoff_delay(self) -> None:
        policy = RetryPolicy(backoff_factor=0.5)
        assert policy.get_delay(0) == 0.5
        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0

    def test_retry_after_override(self) -> None:
        policy = RetryPolicy()
        assert policy.get_delay(0, retry_after=30.0) == 30.0

    def test_raise_for_status_429(self) -> None:
        policy = RetryPolicy()
        with pytest.raises(BoostyRateLimitError):
            policy.raise_for_status(429, "too many requests")

    def test_raise_for_status_500(self) -> None:
        policy = RetryPolicy()
        with pytest.raises(BoostyServerError):
            policy.raise_for_status(500, "internal server error")
