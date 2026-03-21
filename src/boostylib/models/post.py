"""Post and related models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from boostylib.enums import ContentType, PostAccess


class ContentBlock(BaseModel):
    """A single content block within a post."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    type: ContentType
    content: str | None = None
    url: str | None = None
    signed_url: str | None = None
    modificator: str | None = None
    modifications: dict[str, Any] | None = None


class AccessLevel(BaseModel):
    """Post access level configuration."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    level_id: str | None = None
    name: str = "Free"
    price: int = 0
    currency: str = "RUB"
    is_free: bool = True


class PostTag(BaseModel):
    """A tag on a post."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    id: int
    title: str = ""

    def __str__(self) -> str:
        return self.title


class Post(BaseModel):
    """A Boosty blog post."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: str
    title: str = ""
    content: list[ContentBlock] = Field(default=[], alias="data")
    created_at: datetime | int | None = Field(default=None, alias="createdAt")
    updated_at: datetime | int | None = Field(default=None, alias="updatedAt")
    access_level: AccessLevel | None = None
    tags: list[PostTag] = []
    comments_count: int = 0
    is_published: bool = Field(default=True, alias="isPublished")
    price: int = 0
    int_id: int | None = Field(default=None, alias="intId")
    has_access: bool = Field(default=True, alias="hasAccess")
    donations: int = 0
    donators: dict[str, Any] | None = None

    @property
    def tag_names(self) -> list[str]:
        """Get tag titles as strings."""
        return [t.title for t in self.tags]


class PostCreateRequest(BaseModel):
    """Request body for creating a post."""

    title: str
    content: list[ContentBlock]
    access_type: PostAccess = PostAccess.FREE
    access_level_id: str | None = None
    minimum_donation_amount: int | None = None
    minimum_donation_currency: str = "RUB"
    tags: list[str] = []
    teaser: str | None = None
    scheduled_at: datetime | None = None
