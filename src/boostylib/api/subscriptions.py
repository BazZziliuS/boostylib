"""Subscriptions API."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from boostylib.api.base import BaseAPI
from boostylib.models.subscriber import Subscriber
from boostylib.models.subscription import SubscriptionLevel, SubscriptionStatus


class SubscriptionsAPI(BaseAPI):
    """Endpoints for subscription-related operations."""

    async def get_levels(
        self,
        username: str,
        *,
        show_free: bool = True,
    ) -> list[SubscriptionLevel]:
        """Get subscription levels for a blog."""
        data = await self._get(
            f"/blog/{username}/subscription_level/",
            params={"show_free_level": show_free},
        )
        items = data.get("data", data) if isinstance(data, dict) else data
        if isinstance(items, list):
            return [SubscriptionLevel.model_validate(item) for item in items]
        return []

    async def verify_subscription(
        self,
        username: str,
        user_id: str,
    ) -> SubscriptionStatus:
        """Verify a user's subscription status to a blog.

        Iterates through the subscriber list to find the user.
        """
        offset: int = 0
        limit = 100
        while True:
            data = await self._get(
                f"/blog/{username}/subscribers",
                params={"limit": limit, "offset": offset},
            )
            subscribers = data.get("data", [])
            total = data.get("total", 0)

            for sub in subscribers:
                if str(sub.get("id")) == str(user_id):
                    level_data = sub.get("level", {})
                    level = SubscriptionLevel.model_validate(level_data)
                    return SubscriptionStatus(
                        is_subscribed=True,
                        level=level,
                        is_paid=level.price > 0,
                        price=level.price,
                        currency=level.currency,
                    )

            offset += limit
            if not subscribers or offset >= total:
                break

        return SubscriptionStatus(is_subscribed=False)

    async def get_subscribers(
        self,
        username: str,
        *,
        level_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Subscriber]:
        """Get subscribers list with full data (email, payments, status).

        Returns:
            List of Subscriber models with email, payments, and level info.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if level_id is not None:
            params["level_id"] = level_id
        data = await self._get(f"/blog/{username}/subscribers", params=params)
        return [Subscriber.model_validate(item) for item in data.get("data", [])]

    async def get_subscribers_raw(
        self,
        username: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Get raw subscribers response (includes total, offset)."""
        return await self._get(
            f"/blog/{username}/subscribers",
            params={"limit": limit, "offset": offset},
        )

    async def iter_subscribers(
        self,
        username: str,
        *,
        level_id: int | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Subscriber]:
        """Async iterate over all subscribers."""
        offset = 0
        while True:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if level_id is not None:
                params["level_id"] = level_id

            data = await self._get(f"/blog/{username}/subscribers", params=params)
            subscribers = data.get("data", [])
            total = data.get("total", 0)

            for item in subscribers:
                yield Subscriber.model_validate(item)

            offset += limit
            if not subscribers or offset >= total:
                break

    async def create_level(
        self,
        username: str,
        *,
        name: str,
        price: int,
        description: str = "",
        subscribers_limit: int = 0,
        is_thank_msg_enabled: bool = False,
    ) -> SubscriptionLevel:
        """Create a new subscription level."""
        text_block = {
            "type": "text",
            "content": json.dumps([description, "unstyled", []]),
            "modificator": "",
        }
        end_block = {"type": "text", "content": "", "modificator": "BLOCK_END"}

        form_data = {
            "name": name,
            "price": str(price),
            "subscribers_limit": str(subscribers_limit),
            "data": json.dumps([text_block, end_block]),
            "is_thank_msg_enabled": str(is_thank_msg_enabled).lower(),
            "discord_role_id": "",
            "tg_group_ids": "",
        }

        response = await self._transport.request(
            "POST",
            f"/blog/{username}/subscription/level",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        return SubscriptionLevel.model_validate(data)

    async def delete_level(
        self,
        username: str,
        level_id: int,
        *,
        posts_migration_level_id: int = 0,
        subscribers_migration_level_id: int | None = None,
    ) -> None:
        """Delete a subscription level."""
        form_data: dict[str, str] = {
            "posts_migration_level_id": str(posts_migration_level_id),
        }
        if subscribers_migration_level_id is not None:
            form_data["subscribers_migration_level_id"] = str(subscribers_migration_level_id)

        await self._transport.request(
            "DELETE",
            f"/blog/{username}/subscription/level/{level_id}",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
