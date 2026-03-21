"""Event poller: periodically polls API to detect new events."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from boostylib.enums import EventType
from boostylib.events.dispatcher import EventDispatcher
from boostylib.events.models import CommentEvent, SubscriptionEvent
from boostylib.models.user import User

if TYPE_CHECKING:
    from boostylib.api.comments import CommentsAPI
    from boostylib.api.posts import PostsAPI
    from boostylib.api.subscriptions import SubscriptionsAPI
    from boostylib.config import BoostySettings

logger = logging.getLogger("boostylib.events")


class EventPoller:
    """Polls Boosty API at intervals to detect new events.

    Tracks state between polls to detect:
    - New comments on posts
    - New subscribers
    - Subscriber cancellations (disappeared from list)

    Args:
        settings: Boosty settings (for poll_interval).
        dispatcher: Event dispatcher to send detected events to.
        blog_username: Blog to poll.
        posts_api: PostsAPI instance.
        subscriptions_api: SubscriptionsAPI instance.
        comments_api: CommentsAPI instance.
    """

    def __init__(
        self,
        *,
        settings: BoostySettings,
        dispatcher: EventDispatcher,
        blog_username: str = "",
        posts_api: PostsAPI | None = None,
        subscriptions_api: SubscriptionsAPI | None = None,
        comments_api: CommentsAPI | None = None,
    ) -> None:
        self._settings = settings
        self._dispatcher = dispatcher
        self._blog = blog_username
        self._posts_api = posts_api
        self._subscriptions_api = subscriptions_api
        self._comments_api = comments_api
        self._task: asyncio.Task[None] | None = None
        self._running = False

        # State tracking
        self._known_subscriber_ids: set[int] = set()
        self._known_comment_ids: dict[str, set[str]] = {}  # post_id -> set of comment UUIDs
        self._last_poll_time: float = 0
        self._initialized = False

    async def start(self) -> None:
        """Start the polling loop."""
        if self._running:
            return
        if not self._blog:
            logger.warning("Cannot start polling: blog_username not set")
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(
            "Event poller started (interval=%.1fs, blog=%s)",
            self._settings.poll_interval,
            self._blog,
        )

    async def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        logger.info("Event poller stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        # Initial state snapshot (don't emit events for existing data)
        await self._snapshot_initial_state()
        self._initialized = True

        while self._running:
            try:
                await self._poll_subscribers()
                await self._poll_comments()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error during poll cycle")

            await asyncio.sleep(self._settings.poll_interval)

    async def _snapshot_initial_state(self) -> None:
        """Capture initial state so we only emit events for NEW changes."""
        logger.debug("Taking initial state snapshot")

        # Snapshot subscribers
        if self._subscriptions_api:
            try:
                raw = await self._subscriptions_api.get_subscribers_raw(self._blog, limit=500)
                for sub in raw.get("data", []):
                    self._known_subscriber_ids.add(sub["id"])
                logger.debug("Initial subscribers: %d", len(self._known_subscriber_ids))
            except Exception:
                logger.exception("Failed to snapshot subscribers")

        # Snapshot recent post comment IDs
        if self._posts_api and self._comments_api:
            try:
                page = await self._posts_api.list_posts(self._blog, limit=10)
                for post in page.data:
                    comment_page = await self._comments_api.get_comments(
                        self._blog, post.id, limit=50
                    )
                    self._known_comment_ids[post.id] = {c.id for c in comment_page.data}
                logger.debug("Initial comments tracked for %d posts", len(self._known_comment_ids))
            except Exception:
                logger.exception("Failed to snapshot comments")

    async def _poll_subscribers(self) -> None:
        """Detect new and cancelled subscribers."""
        if not self._subscriptions_api:
            return

        try:
            raw = await self._subscriptions_api.get_subscribers_raw(self._blog, limit=500)
            current_subs: dict[int, dict[str, Any]] = {}
            for sub in raw.get("data", []):
                current_subs[sub["id"]] = sub

            current_ids = set(current_subs.keys())

            # New subscribers
            new_ids = current_ids - self._known_subscriber_ids
            for uid in new_ids:
                sub_data = current_subs[uid]
                level_data = sub_data.get("level", {})
                await self._dispatcher.dispatch(
                    SubscriptionEvent(
                        type=EventType.NEW_SUBSCRIPTION,
                        blog_username=self._blog,
                        timestamp=datetime.now(UTC),
                        user=User(id=uid, name=sub_data.get("name", "")),
                        level=level_data,
                    )
                )
                logger.info("New subscriber: %s (id=%d)", sub_data.get("name", ""), uid)

            # Cancelled subscribers
            gone_ids = self._known_subscriber_ids - current_ids
            for uid in gone_ids:
                await self._dispatcher.dispatch(
                    SubscriptionEvent(
                        type=EventType.SUBSCRIPTION_CANCELLED,
                        blog_username=self._blog,
                        timestamp=datetime.now(UTC),
                        user=User(id=uid, name=""),
                        level={},
                    )
                )
                logger.info("Subscriber cancelled: id=%d", uid)

            self._known_subscriber_ids = current_ids

        except Exception:
            logger.exception("Error polling subscribers")

    async def _poll_comments(self) -> None:
        """Detect new comments on recent posts."""
        if not self._posts_api or not self._comments_api:
            return

        try:
            page = await self._posts_api.list_posts(self._blog, limit=10)
            for post in page.data:
                comment_page = await self._comments_api.get_comments(self._blog, post.id, limit=50)
                known = self._known_comment_ids.get(post.id, set())

                for comment in comment_page.data:
                    if comment.id not in known:
                        await self._dispatcher.dispatch(
                            CommentEvent(
                                type=EventType.NEW_COMMENT,
                                blog_username=self._blog,
                                timestamp=datetime.now(UTC),
                                user=comment.author,
                                post_id=post.id,
                                comment_id=comment.id,
                                content=comment.content
                                if isinstance(comment.content, str)
                                else comment.text,
                            )
                        )
                        logger.info("New comment on %s by %s", post.id, comment.author.name)

                self._known_comment_ids[post.id] = {c.id for c in comment_page.data}

        except Exception:
            logger.exception("Error polling comments")
