"""HTTP status code specific exceptions."""

from __future__ import annotations

from boostylib.http.exceptions.base import BoostyError


class BoostyAuthError(BoostyError):
    """401 Unauthorized — invalid or expired token."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, status_code=401)


class BoostyForbiddenError(BoostyError):
    """403 Forbidden — insufficient permissions."""

    def __init__(self, message: str = "Access forbidden") -> None:
        super().__init__(message, status_code=403)


class BoostyNotFoundError(BoostyError):
    """404 Not Found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class BoostyRateLimitError(BoostyError):
    """429 Too Many Requests."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class BoostyServerError(BoostyError):
    """5xx Server Error."""

    def __init__(self, message: str = "Server error", *, status_code: int = 500) -> None:
        super().__init__(message, status_code=status_code)
