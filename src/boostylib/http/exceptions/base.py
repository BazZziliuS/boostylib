"""Base exception for Boosty API errors."""

from __future__ import annotations


class BoostyError(Exception):
    """Base exception for all boostylib errors."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
