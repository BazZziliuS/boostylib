"""E2E tests for targets API — basic read operations."""

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


class TestTargets:
    async def test_create_read_delete_target(
        self, client: BoostyClient, blog_username: str
    ) -> None:
        """Quick round-trip: create, read by ID, delete."""
        target = await client.targets.create_target(
            blog_username,
            description="quick test",
            target_sum=1000,
            target_type=TargetType.MONEY,
        )
        print(f"\n  Created: id={target.id}, sum={target.target_sum}")

        fetched = await client.targets.get_target(target.id)
        assert fetched.id == target.id

        await client.targets.delete_target(target.id)
        print(f"  Deleted: {target.id}")
