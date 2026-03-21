"""User model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Boosty user."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: int
    name: str = ""
    email: str | None = None
    avatar_url: str | None = Field(default=None, alias="avatarUrl")
    has_avatar: bool = Field(default=False, alias="hasAvatar")
    is_official: bool = Field(default=False, alias="isOfficial")
