"""E2E tests for target lifecycle: create → read → delete."""

from __future__ import annotations

import os

import pytest

from boostylib import BoostyClient
from boostylib.enums import TargetType

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("BOOSTY_ACCESS_TOKEN"),
        reason="BOOSTY_ACCESS_TOKEN not set",
    ),
]


class TestTargetLifecycle:
    async def test_create_money_target_and_delete(
        self, client: BoostyClient, blog_username: str
    ) -> None:
        """Create a money target, read it back, then delete."""
        created = await client.targets.create_target(
            blog_username,
            description="boostylib test money goal",
            target_sum=5000,
            target_type=TargetType.MONEY,
        )
        print(f"\n  Created money target: id={created.id}")
        print(f"  Description: {created.description}")
        print(f"  Target: {created.target_sum}, Current: {created.current_sum}")
        assert created.id
        assert created.target_sum == 5000

        try:
            # Read back by ID
            fetched = await client.targets.get_target(created.id)
            assert fetched.id == created.id
            assert fetched.description == "boostylib test money goal"
            print(f"  Fetched back: {fetched.description} (type={fetched.target_type})")
        finally:
            await client.targets.delete_target(created.id)
            print(f"  Deleted target: {created.id}")

    async def test_create_subscribers_target_and_delete(
        self, client: BoostyClient, blog_username: str
    ) -> None:
        """Create a subscribers target, read it back, then delete."""
        created = await client.targets.create_target(
            blog_username,
            description="boostylib test subscriber goal",
            target_sum=100,
            target_type=TargetType.SUBSCRIBERS,
        )
        print(f"\n  Created subscriber target: id={created.id}")
        print(f"  Target: {created.target_sum} subscribers")
        assert created.id
        assert created.target_sum == 100

        try:
            fetched = await client.targets.get_target(created.id)
            assert fetched.id == created.id
            print(f"  Fetched back: type={fetched.target_type}")
        finally:
            await client.targets.delete_target(created.id)
            print(f"  Deleted target: {created.id}")
