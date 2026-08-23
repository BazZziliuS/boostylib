"""Posts API — two-step draft → publish flow."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from boostylib.api.base import BaseAPI
from boostylib.models.pagination import PaginatedResponse
from boostylib.models.post import Post, PostCreateRequest


class PostsAPI(BaseAPI):
    """Endpoints for post CRUD operations.

    Post creation uses Boosty's two-step flow:
    1. ``PUT /blog/{name}/post_draft`` — save draft
    2. ``POST /blog/{name}/post_draft/publish/`` — publish draft
    """

    async def list_posts(
        self,
        username: str,
        *,
        limit: int = 20,
        offset: str | None = None,
        level_id: str | None = None,
        tags_ids: list[str] | None = None,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> PaginatedResponse[Post]:
        """List posts with filtering and pagination."""
        params: dict[str, Any] = {"limit": limit}
        if offset is not None:
            params["offset"] = offset
        if level_id is not None:
            params["level_id"] = level_id
        if tags_ids is not None:
            params["tags_ids"] = ",".join(tags_ids)
        if from_ts is not None:
            params["from_ts"] = from_ts
        if to_ts is not None:
            params["to_ts"] = to_ts

        data = await self._get(f"/blog/{username}/post/", params=params)
        return self._parse_paginated(data, Post)

    async def iter_posts(
        self,
        username: str,
        *,
        limit: int = 20,
        level_id: str | None = None,
    ) -> AsyncIterator[Post]:
        """Async iterate over all posts."""
        params: dict[str, Any] = {}
        if level_id is not None:
            params["level_id"] = level_id
        async for post in self._iter_pages(
            f"/blog/{username}/post/", Post, params=params, limit=limit
        ):
            yield post

    async def get_post(self, username: str, post_id: str) -> Post:
        """Get a single post by ID."""
        data = await self._get(f"/blog/{username}/post/{post_id}")
        return Post.model_validate(data)

    async def create_post(
        self,
        username: str,
        post: PostCreateRequest,
        *,
        is_showcase_visible: bool = True,
    ) -> Post:
        """Create and publish a post (draft → publish).

        Args:
            username: Blog username.
            post: Post content and settings.
            is_showcase_visible: Show in showcase after publishing.

        Returns:
            The published Post.
        """
        # Step 1: Save draft
        form_data = self._build_draft_form(post)
        await self._transport.request(
            "PUT",
            f"/blog/{username}/post_draft",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Step 2: Publish
        response = await self._transport.request(
            "POST",
            f"/blog/{username}/post_draft/publish/",
            data={"is_showcase_visible": str(is_showcase_visible).lower()},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        post_data = data.get("data", {}).get("post", data)
        return Post.model_validate(post_data)

    async def save_draft(self, username: str, post: PostCreateRequest) -> dict[str, Any]:
        """Save a post as draft without publishing.

        Returns:
            Raw draft response data.
        """
        form_data = self._build_draft_form(post)
        response = await self._transport.request(
            "PUT",
            f"/blog/{username}/post_draft",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return response.json()

    async def publish_draft(
        self,
        username: str,
        *,
        is_showcase_visible: bool = True,
    ) -> Post:
        """Publish the current draft.

        Returns:
            The published Post.
        """
        response = await self._transport.request(
            "POST",
            f"/blog/{username}/post_draft/publish/",
            data={"is_showcase_visible": str(is_showcase_visible).lower()},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        post_data = data.get("data", {}).get("post", data)
        return Post.model_validate(post_data)

    async def update_post(self, username: str, post_id: str, post: PostCreateRequest) -> Post:
        """Update an existing post."""
        form_data = self._build_draft_form(post)
        response = await self._transport.request(
            "PUT",
            f"/blog/{username}/post/{post_id}",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        return Post.model_validate(data.get("data", {}).get("post", data))

    async def delete_post(self, username: str, post_id: str) -> None:
        """Delete a post.

        Args:
            username: Blog username.
            post_id: Identifier of post to delete.
        """
        await self._transport.request("DELETE", f"/blog/{username}/post/{post_id}")

    def _build_draft_form(self, post: PostCreateRequest) -> dict[str, str]:
        """Build form-urlencoded data for the draft endpoint."""
        content_blocks = []
        for block in post.content:
            boosty_block: dict[str, Any] = {"type": block.type.value}
            if block.type.value == "text":
                raw_text = block.content or ""
                boosty_block["content"] = json.dumps([raw_text, "unstyled", []])
                boosty_block["modificator"] = ""
            else:
                boosty_block["content"] = block.content or ""
                if block.url:
                    boosty_block["url"] = block.url
            content_blocks.append(boosty_block)

        # Append BLOCK_END
        content_blocks.append({"type": "text", "content": "", "modificator": "BLOCK_END"})

        form: dict[str, str] = {
            "title": post.title,
            "data": json.dumps(content_blocks),
            "price": str(post.minimum_donation_amount or 0),
            "teaser_data": json.dumps([]),
            "tags": ",".join(post.tags) if post.tags else "",
            "deny_comments": "false",
            "deny_reactions": "false",
            "wait_video": "false",
            "advertiser_info": "",
            "bundle_ids": "",
        }
        if post.scheduled_at is not None:
            form["publish_time"] = str(int(post.scheduled_at.timestamp()))
        return form
