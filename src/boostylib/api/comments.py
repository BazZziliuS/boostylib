"""Comments API."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from boostylib.api.base import BaseAPI
from boostylib.enums import CommentOrder
from boostylib.models.comment import Comment
from boostylib.models.pagination import PaginatedResponse


class CommentsAPI(BaseAPI):
    """Endpoints for comment operations."""

    async def get_comments(
        self,
        username: str,
        post_id: str,
        *,
        limit: int = 20,
        offset: str | None = None,
        reply_limit: int = 2,
        order: CommentOrder = CommentOrder.DESC,
    ) -> PaginatedResponse[Comment]:
        """Get comments for a post."""
        params: dict[str, Any] = {
            "limit": limit,
            "reply_limit": reply_limit,
            "order": order.value,
        }
        if offset is not None:
            params["offset"] = offset

        data = await self._get(f"/blog/{username}/post/{post_id}/comment/", params=params)
        return self._parse_comments(data)

    async def create_comment(
        self,
        username: str,
        post_id: str,
        text: str,
        *,
        reply_to: str | None = None,
    ) -> Comment:
        """Create a comment on a post.

        Args:
            username: Blog username.
            post_id: Post ID.
            text: Comment text.
            reply_to: Comment ID to reply to (optional).
        """
        text_block = {
            "type": "text",
            "content": json.dumps([text, "unstyled", []]),
            "modificator": "",
        }
        end_block = {"type": "text", "content": "", "modificator": "BLOCK_END"}

        form_data: dict[str, str] = {
            "data": json.dumps([text_block, end_block]),
        }
        if reply_to is not None:
            form_data["reply_id"] = reply_to

        response = await self._transport.request(
            "POST",
            f"/blog/{username}/post/{post_id}/comment/",
            params={"from_page": "blog"},
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        raw = response.json()
        return self._parse_single_comment(raw)

    async def delete_comment(
        self,
        username: str,
        post_id: str,
        comment_id: str,
    ) -> None:
        """Delete a comment.

        Args:
            username: Blog username.
            post_id: Post ID.
            comment_id: Comment UUID to delete.
        """
        await self._transport.request(
            "DELETE",
            f"/blog/{username}/post/{post_id}/comment/{comment_id}",
            params={"from_page": "blog"},
        )

    async def iter_comments(
        self,
        username: str,
        post_id: str,
        *,
        limit: int = 20,
        order: CommentOrder = CommentOrder.DESC,
    ) -> AsyncIterator[Comment]:
        """Async iterate over all comments for a post."""
        offset: str | None = None
        while True:
            page = await self.get_comments(
                username,
                post_id,
                limit=limit,
                offset=offset,
                order=order,
            )
            for comment in page.data:
                yield comment
            if page.is_last or page.cursor is None:
                break
            offset = page.cursor

    def _parse_comments(self, data: dict[str, Any]) -> PaginatedResponse[Comment]:
        """Parse the comments response into Comment models."""
        raw_items = data.get("data", [])
        extra = data.get("extra", {})
        comments = [self._parse_single_comment(item) for item in raw_items]
        return PaginatedResponse(
            data=comments,
            cursor=extra.get("offset"),
            is_last=extra.get("isLast", True),
        )

    def _parse_single_comment(self, raw: dict[str, Any]) -> Comment:
        """Parse a single comment from raw API data."""
        # Extract text from Draft.js content blocks
        content_blocks = raw.get("data", [])
        text_parts: list[str] = []
        for block in content_blocks:
            if block.get("type") == "text" and block.get("modificator") != "BLOCK_END":
                raw_content = block.get("content", "")
                try:
                    parsed = json.loads(raw_content)
                    if isinstance(parsed, list) and parsed:
                        text_parts.append(str(parsed[0]))
                except json.JSONDecodeError, IndexError:
                    if raw_content:
                        text_parts.append(raw_content)

        author_data = raw.get("author", {})
        return Comment(
            id=str(raw.get("id", "")),
            intId=raw.get("intId"),
            author=author_data,
            content="\n".join(text_parts),
            createdAt=raw.get("createdAt"),
            replyId=raw.get("replyId"),
        )
