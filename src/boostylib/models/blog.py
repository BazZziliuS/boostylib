"""Blog model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from boostylib.models.user import User


class BlogCount(BaseModel):
    """Blog entity counts."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    posts: int = 0
    subscribers: int = 0
    showcase: int = 0


class Blog(BaseModel):
    """Boosty blog/channel info."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    blog_url: str = Field(default="", alias="blogUrl")
    title: str = ""
    description: list[dict[str, Any]] | str = ""
    owner: User | None = None
    count: BlogCount = BlogCount()
    is_subscribed: bool = Field(default=False, alias="isSubscribed")
    is_owner: bool = Field(default=False, alias="isOwner")
    has_adult_content: bool = Field(default=False, alias="hasAdultContent")
    cover_url: str | None = Field(default=None, alias="coverUrl")
    currency: str = "RUB"

    @property
    def url(self) -> str:
        return self.blog_url

    @property
    def subscriber_count(self) -> int:
        return self.count.subscribers

    @property
    def post_count(self) -> int:
        return self.count.posts
