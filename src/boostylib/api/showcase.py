"""Showcase API."""

from __future__ import annotations

from typing import Any

from boostylib.api.base import BaseAPI


class ShowcaseAPI(BaseAPI):
    """Endpoints for blog showcase."""

    async def get_showcase(self, username: str) -> list[dict[str, Any]]:
        """Get showcase items.

        Args:
            username: Blog username.

        Returns:
            List of showcase item dictionaries.
        """
        data = await self._get(f"/blog/{username}/showcase/")
        if isinstance(data, dict):
            return data.get("data", [])
        return data if isinstance(data, list) else []

    async def set_showcase_status(self, username: str, *, status: str) -> None:
        """Set showcase visibility status.

        Args:
            username: Blog username.
            status: Status value to set.
        """
        await self._put(f"/blog/{username}/showcase/status", json={"status": status})
