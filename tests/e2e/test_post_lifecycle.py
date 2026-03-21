"""E2E tests for full post lifecycle: create → read → update → delete."""

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


class TestPostLifecycle:
    async def test_create_read_delete(self, client: BoostyClient, blog_username: str) -> None:
        """Full lifecycle: create a post, read it back, then delete it."""

        # Create
        post_req = (
            PostBuilder()
            .title("boostylib E2E Test Post")
            .text("This post was created by boostylib automated tests.")
            .text("It will be deleted immediately after verification.")
            .free()
            .tags(["test", "boostylib"])
            .build()
        )

        created = await client.posts.create_post(blog_username, post_req)
        print(f"\n  Created post: {created.id}")
        print(f"  Title: {created.title}")
        print(f"  Published: {created.is_published}")
        assert created.id
        assert created.title == "boostylib E2E Test Post"
        assert created.is_published is True

        post_id = created.id

        try:
            # Read back
            fetched = await client.posts.get_post(blog_username, post_id)
            print(f"  Fetched back: {fetched.title} (id={fetched.id})")
            assert fetched.id == post_id
            assert fetched.title == "boostylib E2E Test Post"

            # Verify it appears in the list
            page = await client.posts.list_posts(blog_username, limit=5)
            post_ids = [p.id for p in page.data]
            assert post_id in post_ids, f"Created post {post_id} not in list: {post_ids}"
            print(f"  Confirmed in post list")
        finally:
            # Delete (always clean up)
            await client.posts.delete_post(blog_username, post_id)
            print(f"  Deleted post: {post_id}")

    async def test_save_draft_then_publish(self, client: BoostyClient, blog_username: str) -> None:
        """Test two-step flow: save draft, then publish separately."""

        post_req = (
            PostBuilder()
            .title("boostylib Draft Test")
            .text("This is a draft that will be published separately.")
            .free()
            .build()
        )

        # Save as draft
        draft_data = await client.posts.save_draft(blog_username, post_req)
        print(f"\n  Draft saved: {draft_data.get('data', {}).get('postDraft', {}).get('title', '?')}")

        # Publish
        published = await client.posts.publish_draft(blog_username)
        print(f"  Published: {published.id} — {published.title}")
        assert published.is_published is True

        # Clean up
        await client.posts.delete_post(blog_username, published.id)
        print(f"  Deleted: {published.id}")
