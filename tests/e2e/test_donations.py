"""E2E tests for donation messages from dialogs."""

from __future__ import annotations

import os

import pytest

from boostylib import BoostyClient
from boostylib.api.donations import DonationMessage

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("BOOSTY_ACCESS_TOKEN"),
        reason="BOOSTY_ACCESS_TOKEN not set",
    ),
]


class TestDonations:
    async def test_get_donation_messages(self, client: BoostyClient) -> None:
        """Get donation messages from dialogs."""
        donations = await client.donations.get_donation_messages(limit=20)
        print(f"\n  Donation messages: {len(donations)}")
        for d in donations[:5]:
            assert isinstance(d, DonationMessage)
            assert d.amount > 0
            print(f"    {d.user.name} ({d.email}): {d.amount} RUB")
            print(f"      Message: {d.message or '(none)'}")

    async def test_iter_donation_messages(self, client: BoostyClient) -> None:
        """Iterate over donation messages."""
        count = 0
        async for d in client.donations.iter_donation_messages(limit=10):
            count += 1
            assert d.amount > 0
            if count >= 15:
                break
        print(f"\n  Iterated over {count} donation messages")

    async def test_get_dialog_donations(self, client: BoostyClient) -> None:
        """Get all donations from a single dialog (multiple from same user)."""
        # First find a dialog with donations
        donations = await client.donations.get_donation_messages(limit=5)
        if not donations:
            pytest.skip("No donation messages found")

        dialog_id = donations[0].dialog_id
        assert dialog_id is not None

        all_in_dialog = await client.donations.get_dialog_donations(dialog_id)
        print(f"\n  Dialog {dialog_id}: {len(all_in_dialog)} donations")
        for d in all_in_dialog[:5]:
            print(f"    {d.amount} RUB: {d.message or '(none)'}")
        assert len(all_in_dialog) >= 1
