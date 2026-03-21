"""Tests for PostBuilder."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from boostylib.builders.post_builder import PostBuilder
from boostylib.enums import ContentType, PostAccess

pytestmark = pytest.mark.unit


class TestPostBuilder:
    def test_free_post(self) -> None:
        post = PostBuilder().title("Test").text("Hello world").free().build()
        assert post.title == "Test"
        assert post.access_type == PostAccess.FREE
        assert len(post.content) == 1
        assert post.content[0].type == ContentType.TEXT
        assert post.content[0].content == "Hello world"

    def test_post_with_subscription_level(self) -> None:
        post = (
            PostBuilder()
            .title("Premium only")
            .text("Secret")
            .access_level(level_id="level_123")
            .build()
        )
        assert post.access_type == PostAccess.SUBSCRIPTION
        assert post.access_level_id == "level_123"

    def test_post_with_minimum_donation(self) -> None:
        post = (
            PostBuilder()
            .title("Donation post")
            .text("Content")
            .minimum_donation(amount=500, currency="RUB")
            .build()
        )
        assert post.access_type == PostAccess.DONATION
        assert post.minimum_donation_amount == 500
        assert post.minimum_donation_currency == "RUB"

    def test_builder_requires_title(self) -> None:
        with pytest.raises(ValueError, match="title"):
            PostBuilder().text("No title").build()

    def test_builder_requires_content(self) -> None:
        with pytest.raises(ValueError, match="content"):
            PostBuilder().title("No content").build()

    def test_multiple_content_blocks(self) -> None:
        post = (
            PostBuilder()
            .title("Multi")
            .text("Intro")
            .image(url="https://example.com/img.png")
            .text("Outro")
            .free()
            .build()
        )
        assert len(post.content) == 3
        assert post.content[0].type == ContentType.TEXT
        assert post.content[1].type == ContentType.IMAGE
        assert post.content[2].type == ContentType.TEXT

    def test_scheduled_post(self) -> None:
        dt = datetime(2026, 4, 1, 12, 0, tzinfo=UTC)
        post = PostBuilder().title("Scheduled").text("Later").free().scheduled_at(dt).build()
        assert post.scheduled_at == dt

    def test_tags(self) -> None:
        post = PostBuilder().title("Tagged").text("Content").tags(["devlog", "update"]).build()
        assert post.tags == ["devlog", "update"]

    def test_teaser(self) -> None:
        post = (
            PostBuilder()
            .title("Premium")
            .text("Hidden")
            .access_level(level_id="lvl1")
            .teaser("Subscribe to see this")
            .build()
        )
        assert post.teaser == "Subscribe to see this"

    def test_subscribers_only(self) -> None:
        post = PostBuilder().title("Subs").text("Content").subscribers_only().build()
        assert post.access_type == PostAccess.SUBSCRIPTION
        assert post.access_level_id is None

    def test_file_block(self) -> None:
        post = (
            PostBuilder()
            .title("With file")
            .text("Download:")
            .file(media_id="file_123", filename="data.zip")
            .build()
        )
        assert len(post.content) == 2
        assert post.content[1].type == ContentType.FILE
        assert post.content[1].url == "file_123"

    def test_link_block(self) -> None:
        post = (
            PostBuilder()
            .title("With link")
            .text("Check out:")
            .link(url="https://example.com", title="Example")
            .build()
        )
        assert post.content[1].type == ContentType.LINK
        assert post.content[1].url == "https://example.com"
        assert post.content[1].content == "Example"
