"""E2E tests for subscriber data including email and payments."""

from __future__ import annotations

import os

import pytest

from boostylib import BoostyClient
from boostylib.models.subscriber import Subscriber

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("BOOSTY_ACCESS_TOKEN"),
        reason="BOOSTY_ACCESS_TOKEN not set",
    ),
]


class TestSubscriberData:
    async def test_get_subscribers_typed(self, client: BoostyClient, blog_username: str) -> None:
        """Get subscribers as typed Subscriber models with email."""
        subs = await client.subscriptions.get_subscribers(blog_username, limit=10)
        print(f"\n  Subscribers ({len(subs)}):")
        for sub in subs:
            assert isinstance(sub, Subscriber)
            assert sub.id > 0
            print(f"    {sub.name} email={sub.email} payments={sub.payments}")
            print(f"      active={sub.is_active} paid={sub.is_paid}")

    async def test_iter_subscribers_typed(self, client: BoostyClient, blog_username: str) -> None:
        """Iterate over subscribers as typed models."""
        count = 0
        async for sub in client.subscriptions.iter_subscribers(blog_username):
            assert isinstance(sub, Subscriber)
            count += 1
        print(f"\n  Iterated over {count} subscribers")

    async def test_subscriber_has_email(self, client: BoostyClient, blog_username: str) -> None:
        """Verify that subscriber data includes email addresses."""
        subs = await client.subscriptions.get_subscribers(blog_username, limit=50)
        with_email = [s for s in subs if s.email]
        print(f"\n  {len(with_email)}/{len(subs)} subscribers have email")
        if subs:
            # At least some subscribers should have emails
            assert len(with_email) > 0, "Expected at least one subscriber with email"
