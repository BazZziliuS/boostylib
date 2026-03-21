"""Donations API — reads donation data from dialogs, posts, and subscribers.

Boosty does not have a dedicated ``/donations/`` endpoint.
Donation messages live in dialogs (``/dialog/``), donation totals
are embedded in posts (``donators``), and lifetime payments
are on subscriber objects (``payments``).
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

from boostylib.api.base import BaseAPI
from boostylib.models.user import User

if TYPE_CHECKING:
    from boostylib.api.subscriptions import SubscriptionsAPI


class DonationMessage(BaseModel):
    """A donation with message, extracted from a dialog."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    amount: float
    user: User
    email: str = ""
    message: str = ""
    created_at: int | None = None
    dialog_id: int | None = None
    donation_id: int | None = None
    is_fee_paid: bool = False


class PostDonationInfo(BaseModel):
    """Donation summary for a specific post."""

    model_config = ConfigDict(frozen=True)

    post_id: str
    post_title: str = ""
    total_amount: int = 0
    donators: list[dict[str, Any]] = []


class PaymentInfo(BaseModel):
    """Payment summary for a subscriber."""

    model_config = ConfigDict(frozen=True)

    user_id: int
    name: str = ""
    email: str = ""
    total_payments: float = 0.0
    is_active: bool = False


class DonationsAPI(BaseAPI):
    """Access donation data from dialogs, posts, and subscribers.

    The primary source for donation messages is ``/dialog/`` — each donation
    creates a dialog entry with the donor's message, amount, email, and timestamp.
    """

    async def get_donation_messages(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[DonationMessage]:
        """Get donation messages from dialogs.

        Returns donations with sender info, amount, message text, and email.
        This is the primary way to see who donated and what they wrote.

        Args:
            limit: Max dialogs to fetch.
            offset: Pagination offset.

        Returns:
            List of DonationMessage sorted by most recent.
        """
        data = await self._get("/dialog/", params={"limit": limit, "offset": offset})
        dialogs = data.get("data", [])
        result: list[DonationMessage] = []

        for dialog in dialogs:
            msg = dialog.get("lastMessage", {})
            donation = msg.get("donation")
            if not donation or donation.get("amount", 0) <= 0:
                continue

            user_data = donation.get("user", {})
            message_text = _extract_text(msg.get("data", []))

            result.append(
                DonationMessage(
                    amount=donation["amount"],
                    user=User.model_validate(user_data),
                    email=user_data.get("email", ""),
                    message=message_text,
                    created_at=donation.get("createdAt"),
                    dialog_id=dialog.get("id"),
                    donation_id=donation.get("id"),
                    is_fee_paid=donation.get("isFeePaid", False),
                )
            )

        return result

    async def iter_donation_messages(
        self, *, limit: int = 20
    ) -> AsyncIterator[DonationMessage]:
        """Async iterate over all donation messages across all dialogs.

        Yields:
            DonationMessage for each dialog that contains a donation.
        """
        offset = 0
        while True:
            data = await self._get(
                "/dialog/", params={"limit": limit, "offset": offset}
            )
            dialogs = data.get("data", [])
            total = data.get("extra", {}).get("total", 0)

            for dialog in dialogs:
                msg = dialog.get("lastMessage", {})
                donation = msg.get("donation")
                if not donation or donation.get("amount", 0) <= 0:
                    continue

                user_data = donation.get("user", {})
                message_text = _extract_text(msg.get("data", []))

                yield DonationMessage(
                    amount=donation["amount"],
                    user=User.model_validate(user_data),
                    email=user_data.get("email", ""),
                    message=message_text,
                    created_at=donation.get("createdAt"),
                    dialog_id=dialog.get("id"),
                    donation_id=donation.get("id"),
                    is_fee_paid=donation.get("isFeePaid", False),
                )

            offset += limit
            if not dialogs or offset >= total:
                break

    async def get_dialog_donations(self, dialog_id: int) -> list[DonationMessage]:
        """Get all donation messages from a specific dialog.

        Each dialog can have multiple donations from the same user.

        Args:
            dialog_id: Dialog ID.

        Returns:
            List of all donations in this dialog.
        """
        data = await self._get(
            f"/dialog/{dialog_id}/message/", params={"limit": 100}
        )
        messages = data.get("data", [])
        result: list[DonationMessage] = []

        for msg in messages:
            donation = msg.get("donation")
            if not donation or donation.get("amount", 0) <= 0:
                continue

            user_data = donation.get("user", {})
            message_text = _extract_text(msg.get("data", []))

            result.append(
                DonationMessage(
                    amount=donation["amount"],
                    user=User.model_validate(user_data),
                    email=user_data.get("email", ""),
                    message=message_text,
                    created_at=donation.get("createdAt"),
                    dialog_id=dialog_id,
                    donation_id=donation.get("id"),
                    is_fee_paid=donation.get("isFeePaid", False),
                )
            )

        return result

    async def get_post_donations(
        self,
        username: str,
        post_id: str,
    ) -> PostDonationInfo:
        """Get donation info for a specific post."""
        data = await self._get(f"/blog/{username}/post/{post_id}")
        return PostDonationInfo(
            post_id=data.get("id", post_id),
            post_title=data.get("title", ""),
            total_amount=data.get("donations", 0),
            donators=data.get("donators", {}).get("data", []),
        )

    async def get_paid_subscribers(
        self,
        username: str,
        *,
        subscriptions_api: SubscriptionsAPI,
    ) -> list[PaymentInfo]:
        """Get all subscribers who have made payments."""
        result: list[PaymentInfo] = []
        async for sub in subscriptions_api.iter_subscribers(username):
            if sub.payments > 0:
                result.append(
                    PaymentInfo(
                        user_id=sub.id,
                        name=sub.name,
                        email=sub.email,
                        total_payments=sub.payments,
                        is_active=sub.is_active,
                    )
                )
        return result


def _extract_text(data_blocks: list[dict[str, Any]]) -> str:
    """Extract plain text from Draft.js content blocks."""
    parts: list[str] = []
    for block in data_blocks:
        if block.get("type") == "text" and block.get("modificator") != "BLOCK_END":
            raw = block.get("content", "")
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list) and parsed:
                    parts.append(str(parsed[0]))
            except (json.JSONDecodeError, IndexError):
                if raw:
                    parts.append(raw)
    return "\n".join(parts)
