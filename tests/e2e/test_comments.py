"""E2E tests for comments API."""

from __future__ import annotations

import os

import pytest

from boostylib import BoostyClient
from boostylib.builders import PostBuilder

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("BOOSTY_ACCESS_TOKEN"),
        reason="BOOSTY_ACCESS_TOKEN not set",
    ),
]


class TestComments:
    async def test_create_and_read_comment(self, client: BoostyClient, blog_username: str) -> None:
        """Create a post, add a comment, read it back, clean up."""

        # Create a post to comment on
        post_req = PostBuilder().title("Comment Test Post").text("Testing comments").free().build()
        post = await client.posts.create_post(blog_username, post_req)
        print(f"\n  Created post: {post.id}")

        try:
            # Create comment
            comment = await client.comments.create_comment(
                blog_username, post.id, "Hello from boostylib tests!"
            )
            print(f"  Created comment: {comment.id}")
            print(f"  Author: {comment.author.name}")
            print(f"  Text: {comment.content}")
            assert comment.id
            assert comment.content == "Hello from boostylib tests!"

            # Read comments
            page = await client.comments.get_comments(blog_username, post.id)
            assert len(page.data) >= 1
            found = any(c.id == comment.id for c in page.data)
            assert found, "Created comment not found in comment list"
            print(f"  Confirmed in comment list ({len(page.data)} comments)")

        finally:
            await client.posts.delete_post(blog_username, post.id)
            print(f"  Deleted post: {post.id}")

    async def test_reply_to_comment(self, client: BoostyClient, blog_username: str) -> None:
        """Create a comment and reply to it."""

        post_req = PostBuilder().title("Reply Test Post").text("Testing replies").free().build()
        post = await client.posts.create_post(blog_username, post_req)
        print(f"\n  Created post: {post.id}")

        try:
            # Create original comment
            original = await client.comments.create_comment(
                blog_username, post.id, "Original comment"
            )
            print(f"  Original: {original.id} — {original.content}")

            # Reply to it (reply_id uses intId, not UUID)
            reply = await client.comments.create_comment(
                blog_username,
                post.id,
                "This is a reply!",
                reply_to=str(original.int_id),
            )
            print(f"  Reply: {reply.id} — {reply.content}")
            assert reply.id
            assert reply.content == "This is a reply!"

        finally:
            await client.posts.delete_post(blog_username, post.id)
            print(f"  Deleted post: {post.id}")

    async def test_auto_reply_scenario(self, client: BoostyClient, blog_username: str) -> None:
        """Simulate auto-reply: create post, detect new comment, auto-respond."""

        post_req = PostBuilder().title("Auto-Reply Test").text("Auto-reply scenario").free().build()
        post = await client.posts.create_post(blog_username, post_req)
        print(f"\n  Created post: {post.id}")

        try:
            # Simulate user comment
            user_comment = await client.comments.create_comment(
                blog_username, post.id, "Great post!"
            )
            print(f"  User comment: {user_comment.content}")

            # Auto-reply logic (what the event handler would do)
            auto_reply = await client.comments.create_comment(
                blog_username,
                post.id,
                f"Thank you, {user_comment.author.name}! Glad you liked it!",
                reply_to=str(user_comment.int_id),
            )
            print(f"  Auto-reply: {auto_reply.content}")
            assert user_comment.author.name in auto_reply.content

            # Verify both comments exist
            page = await client.comments.get_comments(blog_username, post.id)
            assert len(page.data) >= 1  # At least the original (replies may be nested)
            print(f"  Total comments: {len(page.data)}")

        finally:
            await client.posts.delete_post(blog_username, post.id)
            print(f"  Deleted post: {post.id}")
