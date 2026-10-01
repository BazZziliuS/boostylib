"""Tests for Post models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from boostylib.enums import ContentType
from boostylib.models.post import AccessLevel, ContentBlock, Post

pytestmark = pytest.mark.unit


class TestContentBlock:
    def test_text_block(self) -> None:
        block = ContentBlock(type=ContentType.TEXT, content="Hello")
        assert block.type == ContentType.TEXT
        assert block.content == "Hello"
        assert block.url is None

    def test_image_block(self) -> None:
        block = ContentBlock(type=ContentType.IMAGE, url="https://example.com/img.png")
        assert block.type == ContentType.IMAGE
        assert block.url == "https://example.com/img.png"

    def test_frozen(self) -> None:
        block = ContentBlock(type=ContentType.TEXT, content="Hello")
        with pytest.raises(Exception):  # noqa: B017
            block.content = "World"


class TestAccessLevel:
    def test_defaults(self) -> None:
        level = AccessLevel()
        assert level.is_free is True
        assert level.price == 0
        assert level.currency == "RUB"

    def test_premium(self) -> None:
        level = AccessLevel(level_id="abc", name="Premium", price=500, is_free=False)
        assert level.level_id == "abc"
        assert level.is_free is False


class TestPost:
    def test_minimal(self) -> None:
        post = Post(
            id="123",
            title="Test",
            createdAt=datetime(2026, 1, 1, tzinfo=UTC),
        )
        assert post.id == "123"
        assert post.tags == []
        assert post.is_published is True

    def test_with_content(self) -> None:
        from boostylib.models.post import PostTag

        post = Post(
            id="456",
            title="Full post",
            data=[
                ContentBlock(type=ContentType.TEXT, content="Paragraph"),
                ContentBlock(type=ContentType.IMAGE, url="https://img.jpg"),
            ],
            createdAt=datetime(2026, 1, 1, tzinfo=UTC),
            tags=[PostTag(id=1, title="test")],
        )
        assert len(post.content) == 2
        assert post.tag_names == ["test"]
