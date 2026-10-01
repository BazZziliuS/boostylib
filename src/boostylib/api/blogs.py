"""Blogs API."""

from __future__ import annotations

from typing import Any

from boostylib.api.base import BaseAPI
from boostylib.models.blog import Blog


class BlogsAPI(BaseAPI):
    """Endpoints for blog operations."""

    async def get_blog(self, username: str) -> Blog:
        """Get blog information by username.

        Args:
            username: Blog username.

        Returns:
            Blog model instance.
        """
        data = await self._get(f"/blog/{username}")
        return Blog.model_validate(data)

    async def get_blacklist(self, blog_url: str) -> list[dict[str, Any]]:
        """Get blacklisted users for a blog.

        Args:
            blog_url: Blog URL or username.

        Returns:
            List of blacklisted user dictionaries.
        """
        data = await self._get("/blacklist/", params={"blog_url": blog_url})
        return data.get("data", [])
