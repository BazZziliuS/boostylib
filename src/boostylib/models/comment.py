"""Comment model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from boostylib.models.user import User


class Comment(BaseModel):
    """A comment on a post."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: str
    int_id: int | None = Field(default=None, alias="intId")
    author: User
    content: str | list[dict[str, Any]] = ""
    created_at: datetime | int | None = Field(default=None, alias="createdAt")
    reply_to: str | int | None = Field(default=None, alias="replyId")

    @property
    def text(self) -> str:
        """Extract plain text from content (handles both string and block list)."""
        if isinstance(self.content, str):
            return self.content
        parts = []
        for block in self.content:
            if block.get("type") == "text" and block.get("content"):
                parts.append(block["content"])
        return " ".join(parts)
