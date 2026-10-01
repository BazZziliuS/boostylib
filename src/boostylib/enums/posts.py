"""Post-related enumerations."""

from enum import StrEnum


class PostAccess(StrEnum):
    """Post access restriction type."""

    FREE = "free"
    SUBSCRIPTION = "subscription"
    DONATION = "donation"
