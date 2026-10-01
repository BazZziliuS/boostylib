"""Content type enumeration."""

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
