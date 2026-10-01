"""Target-related enumerations."""

from enum import StrEnum


class TargetType(StrEnum):
    """Goal/target type."""

    MONEY = "money"
    SUBSCRIBERS = "subscribers"
