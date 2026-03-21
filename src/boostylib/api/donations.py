"""Donations API — reads donation data from posts and subscribers.

Boosty does not have a dedicated donations endpoint.
Donation data is embedded in:
- Post objects: ``donations`` (total amount) and ``donators`` (list of donors)
- Subscriber objects: ``payments`` (lifetime total)
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from boostylib.api.base import BaseAPI

if TYPE_CHECKING:
    from boostylib.api.posts import PostsAPI
    from boostylib.api.subscriptions import SubscriptionsAPI


class DonationInfo:
    """Donation data extracted from a post."""

    __slots__ = ("donators", "post_id", "post_title", "total_amount")

    def __init__(
        self,
        *,
        post_id: str,
        post_title: str,
        total_amount: int,
        donators: list[dict[str, Any]],
    ) -> None:
        self.post_id = post_id
        self.post_title = post_title
        self.total_amount = total_amount
        self.donators = donators

    def __repr__(self) -> str:
        return (
            f"DonationInfo(post_id={self.post_id!r}, "
            f"total={self.total_amount}, donators={len(self.donators)})"
        )


class PaymentInfo:
    """Payment summary for a subscriber."""

    __slots__ = ("email", "is_active", "name", "total_payments", "user_id")

    def __init__(
        self,
        *,
        user_id: int,
        name: str,
        email: str,
        total_payments: float,
        is_active: bool,
    ) -> None:
        self.user_id = user_id
        self.name = name
        self.email = email
        self.total_payments = total_payments
        self.is_active = is_active

    def __repr__(self) -> str:
        return (
            f"PaymentInfo(user={self.name!r}, payments={self.total_payments}, email={self.email!r})"
        )


class DonationsAPI(BaseAPI):
    """Access donation data from posts and subscriber payments.

    Note:
        Boosty has no dedicated ``/donations/`` endpoint.
        Donation data comes from post ``donators`` fields
        and subscriber ``payments`` totals.
    """

    async def get_post_donations(
        self,
        username: str,
        post_id: str,
    ) -> DonationInfo:
        """Get donation info for a specific post.

        Returns:
            DonationInfo with total amount and list of donators.
        """
        data = await self._get(f"/blog/{username}/post/{post_id}")
        return DonationInfo(
            post_id=data.get("id", post_id),
            post_title=data.get("title", ""),
            total_amount=data.get("donations", 0),
            donators=data.get("donators", {}).get("data", []),
        )

    async def iter_posts_with_donations(
        self,
        username: str,
        *,
        posts_api: PostsAPI,
        limit: int = 20,
    ) -> AsyncIterator[DonationInfo]:
        """Iterate over posts that have received donations.

        Args:
            username: Blog username.
            posts_api: PostsAPI instance (use ``client.posts``).
            limit: Posts per page.

        Yields:
            DonationInfo for each post with donations > 0.
        """
        async for post in posts_api.iter_posts(username, limit=limit):
            info = await self.get_post_donations(username, post.id)
            if info.total_amount > 0 or info.donators:
                yield info

    async def get_paid_subscribers(
        self,
        username: str,
        *,
        subscriptions_api: SubscriptionsAPI,
    ) -> list[PaymentInfo]:
        """Get all subscribers who have made payments.

        Args:
            username: Blog username.
            subscriptions_api: SubscriptionsAPI instance (use ``client.subscriptions``).

        Returns:
            List of PaymentInfo for subscribers with payments > 0.
        """
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
