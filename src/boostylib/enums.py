"""Enums for Boosty API entities."""

from enum import StrEnum


class ContentType(StrEnum):
    """Type of content block in a post."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LINK = "link"
    LIST = "list"
    EMOJI = "emoji"


class PostAccess(StrEnum):
    """Post access restriction type."""

    FREE = "free"
    SUBSCRIPTION = "subscription"
    DONATION = "donation"


class EventType(StrEnum):
    """Types of events detected by the poller."""

    NEW_DONATION = "new_donation"
    NEW_SUBSCRIPTION = "new_subscription"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_LEVEL_CHANGED = "subscription_level_changed"
    NEW_COMMENT = "new_comment"
    NEW_POST = "new_post"


class CommentOrder(StrEnum):
    """Comment sort order."""

    ASC = "asc"
    DESC = "desc"


class ExportFormat(StrEnum):
    """Supported export formats."""

    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    SQLITE = "sqlite"


class TargetType(StrEnum):
    """Goal/target type."""

    MONEY = "money"
    SUBSCRIBERS = "subscribers"
