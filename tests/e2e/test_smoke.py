"""Smoke tests — basic connectivity with real Boosty API."""

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


class TestSmoke:
    async def test_get_current_user(self, client: BoostyClient) -> None:
        """Verify we can authenticate and get the current user."""
        user = await client.users.get_current_user()
        assert user.id is not None
        assert user.name is not None
        print(f"\n  Current user: {user.name} (id={user.id})")

    async def test_get_blog(self, client: BoostyClient, blog_username: str) -> None:
        """Verify we can fetch blog info."""
        blog = await client.blogs.get_blog(blog_username)
        assert blog.blog_url
        print(f"\n  Blog: {blog.title or '(no title)'} (url={blog.blog_url})")
        print(f"  Owner: {blog.owner.name if blog.owner else 'N/A'}")
        print(f"  Posts: {blog.post_count}, Subscribers: {blog.subscriber_count}")

    async def test_get_subscription_levels(self, client: BoostyClient, blog_username: str) -> None:
        """Verify we can fetch subscription levels."""
        levels = await client.subscriptions.get_levels(blog_username)
        assert isinstance(levels, list)
        print(f"\n  Subscription levels ({len(levels)}):")
        for level in levels:
            name = level.name.encode("ascii", "replace").decode()
            print(f"    - {name}: {level.price} {level.currency} (free={level.is_free})")
