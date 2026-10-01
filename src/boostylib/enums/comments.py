"""Comment-related enumerations."""

from enum import StrEnum


class CommentOrder(StrEnum):
    """Comment sort order."""

    ASC = "asc"
    DESC = "desc"
