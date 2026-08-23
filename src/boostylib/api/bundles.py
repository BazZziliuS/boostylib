"""Bundles API."""

from __future__ import annotations

from typing import Any

from boostylib.api.base import BaseAPI


class BundlesAPI(BaseAPI):
    """Endpoints for blog bundles (paid content packages)."""

    async def get_bundles(self, username: str) -> list[dict[str, Any]]:
        """Get bundles for a blog.

        Args:
            username: Blog username.

        Returns:
            List of bundle dictionaries.
        """
        data = await self._get(f"/blog/{username}/bundle/")
        if isinstance(data, dict):
            return data.get("data", [])
        return data if isinstance(data, list) else []

    async def get_bundle(self, username: str, bundle_id: str) -> dict[str, Any]:
        """Get a single bundle by ID.

        Args:
            username: Blog username.
            bundle_id: Identifier of target bundle.

        Returns:
            Dictionary containing bundle data.
        """
        return await self._get(f"/blog/{username}/bundle/{bundle_id}")

    async def delete_bundle(self, username: str, bundle_id: str) -> None:
        """Delete a bundle.

        Args:
            username: Blog username.
            bundle_id: Identifier of bundle to delete.
        """
        await self._transport.request("DELETE", f"/blog/{username}/bundle/{bundle_id}")
