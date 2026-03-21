"""Integration tests for PostsAPI with mocked HTTP."""

from __future__ import annotations

import httpx
import pytest
import respx

from boostylib import BoostyClient
from boostylib.builders import PostBuilder

pytestmark = pytest.mark.integration


class TestPostsAPI:
    @respx.mock
    async def test_list_posts(self, client: BoostyClient) -> None:
        respx.get("https://api.boosty.to/v1/blog/testblog/post/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "post_1",
                            "title": "First post",
                            "createdAt": 1710000000,
                            "data": [{"type": "text", "content": "Hello"}],
                            "tags": [],
                            "comments_count": 0,
                            "isPublished": True,
                        }
                    ],
                    "extra": {"offset": None, "isLast": True},
                },
            )
        )

        result = await client.posts.list_posts("testblog", limit=10)
        assert len(result.data) == 1
        assert result.data[0].id == "post_1"
        assert result.data[0].title == "First post"
        assert result.is_last is True

    @respx.mock
    async def test_create_post(self, client: BoostyClient) -> None:
        respx.put("https://api.boosty.to/v1/blog/testblog/post_draft").mock(
            return_value=httpx.Response(
                200,
                json={"data": {"postDraft": {"title": "Created post", "updatedAt": 1710000000}}},
            )
        )
        respx.post("https://api.boosty.to/v1/blog/testblog/post_draft/publish/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": {
                        "post": {
                            "id": "new_post_1",
                            "title": "Created post",
                            "createdAt": 1710000000,
                            "data": [{"type": "text", "content": "Body"}],
                            "tags": [{"id": 1, "title": "test"}],
                            "isPublished": True,
                            "price": 0,
                        }
                    }
                },
            )
        )

        post = (
            PostBuilder()
            .title("Created post")
            .text("Body")
            .access_level(level_id="lvl_1")
            .tags(["test"])
            .build()
        )
        created = await client.posts.create_post("testblog", post)
        assert created.id == "new_post_1"
        assert created.is_published is True

    @respx.mock
    async def test_delete_post(self, client: BoostyClient) -> None:
        respx.delete("https://api.boosty.to/v1/blog/testblog/post/123").mock(
            return_value=httpx.Response(204)
        )
        await client.posts.delete_post("testblog", "123")
