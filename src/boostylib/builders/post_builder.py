"""Fluent builder for creating posts."""

from __future__ import annotations

from datetime import datetime
from typing import Self

from boostylib.enums import ContentType, PostAccess
from boostylib.models.post import ContentBlock, PostCreateRequest


class PostBuilder:
    """Fluent builder for constructing PostCreateRequest.

    Example::

        post = (
            PostBuilder()
            .title("My Post")
            .text("Hello, world!")
            .image(url="https://example.com/img.png")
            .access_level(level_id="abc123")
            .tags(["devlog", "update"])
            .build()
        )
    """

    def __init__(self) -> None:
        self._title: str | None = None
        self._content: list[ContentBlock] = []
        self._access_type: PostAccess = PostAccess.FREE
        self._access_level_id: str | None = None
        self._min_donation_amount: int | None = None
        self._min_donation_currency: str = "RUB"
        self._tags: list[str] = []
        self._teaser: str | None = None
        self._scheduled_at: datetime | None = None

    def title(self, title: str) -> Self:
        """Set the post title."""
        self._title = title
        return self

    def text(self, content: str) -> Self:
        """Add a text content block."""
        self._content.append(ContentBlock(type=ContentType.TEXT, content=content))
        return self

    def image(
        self,
        *,
        url: str | None = None,
        file_path: str | None = None,
        media_id: str | None = None,
    ) -> Self:
        """Add an image content block."""
        self._content.append(
            ContentBlock(type=ContentType.IMAGE, url=url or media_id or file_path)
        )
        return self

    def video(self, *, url: str | None = None, media_id: str | None = None) -> Self:
        """Add a video content block."""
        self._content.append(ContentBlock(type=ContentType.VIDEO, url=url or media_id))
        return self

    def audio(self, *, url: str | None = None, media_id: str | None = None) -> Self:
        """Add an audio content block."""
        self._content.append(ContentBlock(type=ContentType.AUDIO, url=url or media_id))
        return self

    def file(
        self,
        *,
        media_id: str | None = None,
        filename: str | None = None,
        size: int | None = None,
        file_path: str | None = None,
    ) -> Self:
        """Add a file content block."""
        self._content.append(
            ContentBlock(
                type=ContentType.FILE,
                url=media_id or file_path,
                content=filename,
            )
        )
        return self

    def link(self, *, url: str, title: str | None = None) -> Self:
        """Add a link content block."""
        self._content.append(ContentBlock(type=ContentType.LINK, url=url, content=title))
        return self

    def free(self) -> Self:
        """Set post as free for everyone."""
        self._access_type = PostAccess.FREE
        self._access_level_id = None
        self._min_donation_amount = None
        return self

    def access_level(self, *, level_id: str) -> Self:
        """Restrict post to a subscription level and above."""
        self._access_type = PostAccess.SUBSCRIPTION
        self._access_level_id = level_id
        return self

    def minimum_donation(self, *, amount: int, currency: str = "RUB") -> Self:
        """Restrict post to users who donated at least the specified amount."""
        self._access_type = PostAccess.DONATION
        self._min_donation_amount = amount
        self._min_donation_currency = currency
        return self

    def subscribers_only(self) -> Self:
        """Restrict post to any subscribers (any paid level)."""
        self._access_type = PostAccess.SUBSCRIPTION
        return self

    def tags(self, tags: list[str]) -> Self:
        """Set post tags."""
        self._tags = tags
        return self

    def teaser(self, text: str) -> Self:
        """Set teaser text shown to non-subscribers."""
        self._teaser = text
        return self

    def scheduled_at(self, dt: datetime) -> Self:
        """Schedule the post for later publication."""
        self._scheduled_at = dt
        return self

    def build(self) -> PostCreateRequest:
        """Build the PostCreateRequest.

        Raises:
            ValueError: If title or content is missing.
        """
        if not self._title:
            raise ValueError("Post title is required")
        if not self._content:
            raise ValueError("Post must have at least one content block")

        return PostCreateRequest(
            title=self._title,
            content=self._content,
            access_type=self._access_type,
            access_level_id=self._access_level_id,
            minimum_donation_amount=self._min_donation_amount,
            minimum_donation_currency=self._min_donation_currency,
            tags=self._tags,
            teaser=self._teaser,
            scheduled_at=self._scheduled_at,
        )
