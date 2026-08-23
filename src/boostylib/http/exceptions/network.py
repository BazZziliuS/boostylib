"""Network-level exceptions."""

from __future__ import annotations

from boostylib.http.exceptions.base import BoostyError


class BoostyNetworkError(BoostyError):
    """Network-level errors: timeouts, DNS failures, connection errors."""

    def __init__(self, message: str = "Network error", *, cause: Exception | None = None) -> None:
        super().__init__(message, status_code=None)
        self.__cause__ = cause
