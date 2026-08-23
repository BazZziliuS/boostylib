"""Exception hierarchy for Boosty API errors."""

from boostylib.http.exceptions.base import BoostyError
from boostylib.http.exceptions.http import (
    BoostyAuthError,
    BoostyForbiddenError,
    BoostyNotFoundError,
    BoostyRateLimitError,
    BoostyServerError,
)
from boostylib.http.exceptions.network import BoostyNetworkError

__all__ = [
    "BoostyAuthError",
    "BoostyError",
    "BoostyForbiddenError",
    "BoostyNetworkError",
    "BoostyNotFoundError",
    "BoostyRateLimitError",
    "BoostyServerError",
]
