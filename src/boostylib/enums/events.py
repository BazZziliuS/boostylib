"""Event-related enumerations."""

from enum import StrEnum


class EventType(StrEnum):
    """Types of events detected by the poller."""

    NEW_DONATION = "new_donation"
    NEW_SUBSCRIPTION = "new_subscription"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_LEVEL_CHANGED = "subscription_level_changed"
    NEW_COMMENT = "new_comment"
    NEW_POST = "new_post"
