"""E2E tests for subscription level lifecycle: create → verify → delete."""

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


class TestSubscriptionLifecycle:
    async def test_create_and_delete_level(self, client: BoostyClient, blog_username: str) -> None:
        """Create a subscription level, verify it exists, then delete it."""

        # Get the free level ID for migration target
        levels_before = await client.subscriptions.get_levels(blog_username, show_free=True)
        free_level = next((lvl for lvl in levels_before if lvl.price == 0), None)
        free_level_id = free_level.id if free_level else 0
        print(f"\n  Free level ID for migration: {free_level_id}")

        # Create
        created = await client.subscriptions.create_level(
            blog_username,
            name="boostylib Test Level",
            price=100,
            description="Created by boostylib automated tests",
        )
        print(f"  Created level: {created.name} (id={created.id}, price={created.price})")
        assert created.id
        assert created.name == "boostylib Test Level"
        assert created.price == 100

        try:
            # Verify it appears in the list
            levels_after = await client.subscriptions.get_levels(blog_username)
            level_ids = [lvl.id for lvl in levels_after]
            assert created.id in level_ids, f"Created level {created.id} not in list"
            print(f"  Confirmed in levels list ({len(levels_after)} levels)")
        finally:
            # Delete (always clean up)
            await client.subscriptions.delete_level(
                blog_username,
                created.id,
                subscribers_migration_level_id=free_level_id,
            )
            print(f"  Deleted level: {created.id}")

            # Verify deletion
            levels_final = await client.subscriptions.get_levels(blog_username)
            remaining_ids = [lvl.id for lvl in levels_final]
            assert created.id not in remaining_ids
            print(f"  Confirmed deleted ({len(levels_final)} levels remaining)")
