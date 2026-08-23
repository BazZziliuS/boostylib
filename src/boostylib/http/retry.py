"""Retry policy with exponential backoff."""

from __future__ import annotations

import asyncio
import logging

from boostylib.http.exceptions import BoostyRateLimitError, BoostyServerError

logger = logging.getLogger("boostylib.retry")

RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class RetryPolicy:
    """Configurable retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        backoff_factor: Multiplier for exponential delay.
        retryable_statuses: HTTP status codes that trigger a retry.
    """

    def __init__(
        self,
        *,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retryable_statuses: frozenset[int] = RETRYABLE_STATUS_CODES,
    ) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retryable_statuses = retryable_statuses

    def should_retry(self, status_code: int, attempt: int) -> bool:
        """Check if a request should be retried."""
        return attempt < self.max_retries and status_code in self.retryable_statuses

    def get_delay(self, attempt: int, retry_after: float | None = None) -> float:
        """Calculate delay before next retry attempt."""
        if retry_after is not None:
            return float(retry_after)
        return float(self.backoff_factor * (2**attempt))

    async def wait(self, attempt: int, status_code: int, retry_after: float | None = None) -> None:
        """Wait before retry with logging."""
        delay = self.get_delay(attempt, retry_after)
        logger.info(
            "Retry %d/%d after %.1fs (status %d)",
            attempt + 1,
            self.max_retries,
            delay,
            status_code,
        )
        await asyncio.sleep(delay)

    def raise_for_status(self, status_code: int, body: str) -> None:
        """Raise the appropriate exception for non-retryable failures."""
        if status_code == 429:
            raise BoostyRateLimitError(f"Rate limit exceeded: {body}")
        if status_code >= 500:
            raise BoostyServerError(f"Server error: {body}", status_code=status_code)
