"""Paginated response wrapper."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Paginated API response.

    Args:
        data: List of items on this page.
        cursor: Opaque cursor for the next page (None if last page).
        is_last: Whether this is the last page.
        total: Total number of items (if provided by API).
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    data: list[T]
    cursor: str | None = None
    is_last: bool = True
    total: int | None = None
