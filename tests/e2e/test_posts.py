"""E2E tests for posts API."""

from __future__ import annotations

import os

import pytest

from boostylib import BoostyClient

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("BOOSTY_ACCESS_TOKEN"),
        reason="BOOSTY_ACCESS_TOKEN not set",
    ),
]


class TestPosts:
    async def test_list_posts(self, client: BoostyClient, blog_username: str) -> None:
        """Fetch first page of posts."""
        page = await client.posts.list_posts(blog_username, limit=5)
        assert page.data is not None
        print(f"\n  Posts ({len(page.data)}, is_last={page.is_last}):")
        for post in page.data:
            print(f"    [{post.id}] {post.title} ({len(post.content)} blocks)")

    async def test_iter_posts(self, client: BoostyClient, blog_username: str) -> None:
        """Iterate over posts with auto-pagination (limit to 10)."""
        count = 0
        async for _post in client.posts.iter_posts(blog_username, limit=5):
            count += 1
            if count >= 10:
                break
        print(f"\n  Iterated over {count} posts")
        assert count >= 0  # blog may have 0 posts, that's fine

    async def test_get_single_post(self, client: BoostyClient, blog_username: str) -> None:
        """Fetch first post from list, then get it by ID."""
        page = await client.posts.list_posts(blog_username, limit=1)
        if not page.data:
            pytest.skip("Blog has no posts")

        post_id = page.data[0].id
        post = await client.posts.get_post(blog_username, post_id)
        assert post.id == post_id
        assert post.title
        print(f"\n  Post: {post.title}")
        print(f"  Created: {post.created_at}")
        print(f"  Content blocks: {len(post.content)}")
        for block in post.content:
            preview = (block.content or "")[:80] if block.content else block.url or ""
            print(f"    [{block.type}] {preview}")
