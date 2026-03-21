"""Users API."""

from __future__ import annotations

from typing import Any

from boostylib.api.base import BaseAPI
from boostylib.models.user import User


class UsersAPI(BaseAPI):
    """Endpoints for user-related operations."""

    async def get_current_user(self) -> User:
        """Get the currently authenticated user."""
        data = await self._get("/user/current")
        return User.model_validate(data)

    async def get_subscriptions(
        self,
        *,
        limit: int = 30,
        with_follow: bool = False,
    ) -> list[dict[str, Any]]:
        """Get the current user's subscriptions."""
        data = await self._get(
            "/user/subscriptions",
            params={"limit": limit, "with_follow": with_follow},
        )
        return data.get("data", [])
