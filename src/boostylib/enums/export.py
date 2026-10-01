"""Export-related enumerations."""

from enum import StrEnum


class ExportFormat(StrEnum):
    """Supported export formats."""

    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    SQLITE = "sqlite"
