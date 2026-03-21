"""E2E tests for subscriptions API."""

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


class TestSubscriptions:
    async def test_get_levels(self, client: BoostyClient, blog_username: str) -> None:
        """Fetch subscription levels."""
        levels = await client.subscriptions.get_levels(blog_username)
        assert isinstance(levels, list)
        assert len(levels) > 0, "Expected at least one subscription level"

        for level in levels:
            assert level.name
            assert level.currency
            name = level.name.encode("ascii", "replace").decode()
            print(f"\n  Level: {name} -- {level.price} {level.currency}")

    async def test_get_levels_without_free(self, client: BoostyClient, blog_username: str) -> None:
        """Fetch only paid levels."""
        levels = await client.subscriptions.get_levels(blog_username, show_free=False)
        for level in levels:
            name = level.name.encode("ascii", "replace").decode()
            print(f"\n  Paid level: {name} -- {level.price} {level.currency}")

    async def test_verify_subscription_nonexistent(
        self, client: BoostyClient, blog_username: str
    ) -> None:
        """Verify that a fake user is not subscribed."""
        status = await client.subscriptions.verify_subscription(blog_username, "99999999999")
        assert status.is_subscribed is False
        assert status.level is None
        print("\n  Fake user correctly shows as not subscribed")

    async def test_get_subscribers(self, client: BoostyClient, blog_username: str) -> None:
        """Fetch first page of subscribers as typed models."""
        subscribers = await client.subscriptions.get_subscribers(blog_username, limit=5)
        print(f"\n  Subscribers fetched: {len(subscribers)}")
        for sub in subscribers[:3]:
            level_name = sub.level.name if sub.level else "?"
            print(f"    {sub.name} -- {level_name} (email={sub.email})")
