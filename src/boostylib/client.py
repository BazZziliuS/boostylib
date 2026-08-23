"""Main BoostyClient — facade for all API modules."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, Self

import httpx

from boostylib.api.blogs import BlogsAPI
from boostylib.api.bundles import BundlesAPI
from boostylib.api.comments import CommentsAPI
from boostylib.api.donations import DonationsAPI
from boostylib.api.media import MediaAPI
from boostylib.api.posts import PostsAPI
from boostylib.api.showcase import ShowcaseAPI
from boostylib.api.subscriptions import SubscriptionsAPI
from boostylib.api.targets import TargetsAPI
from boostylib.api.users import UsersAPI
from boostylib.auth.manager import AuthManager
from boostylib.auth.models import AuthCredentials
from boostylib.auth.storage import TokenStorage
from boostylib.cache import CacheBackend, CacheManager
from boostylib.config import BoostySettings
from boostylib.enums import EventType
from boostylib.events.dispatcher import EventDispatcher, EventHandler
from boostylib.events.poller import EventPoller
from boostylib.http.middleware import MiddlewareChain
from boostylib.http.transport import HTTPTransport


class BoostyClient:
    """Main client for the Boosty.to API.

    Provides access to all API modules, event system, and caching.

    Example::

        async with BoostyClient(access_token="...") as client:
            user = await client.users.get_current_user()
            print(user.name)

    Args:
        access_token: Static access token (no auto-refresh).
        credentials: Full credentials for auto-refresh.
        token_storage: Custom token storage backend.
        settings: Client configuration.
        http_client: Custom httpx.AsyncClient (for testing or proxies).
        middleware: List of middleware instances.
        cache: Custom cache backend (default: MemoryCache if enabled).
        blog_username: Blog username for event polling.
    """

    def __init__(
        self,
        *,
        access_token: str | None = None,
        credentials: AuthCredentials | None = None,
        token_storage: TokenStorage | None = None,
        settings: BoostySettings | None = None,
        http_client: httpx.AsyncClient | None = None,
        middleware: list[Any] | None = None,
        cache: CacheBackend | None = None,
        blog_username: str = "",
    ) -> None:
        self._settings = settings or BoostySettings()
        self._middleware_chain = MiddlewareChain(middleware)

        # Auth
        self._auth_manager = AuthManager(
            settings=self._settings,
            token_storage=token_storage,
            credentials=credentials,
            access_token=access_token,
        )

        # Transport
        self._transport = HTTPTransport(
            settings=self._settings,
            auth_manager=self._auth_manager,
            http_client=http_client,
            middleware_chain=self._middleware_chain,
        )

        # Cache
        self.cache = CacheManager(
            backend=cache,
            enabled=self._settings.cache_enabled,
            ttl_blog=self._settings.cache_ttl_blog,
            ttl_levels=self._settings.cache_ttl_levels,
            ttl_user=self._settings.cache_ttl_user,
            ttl_default=self._settings.cache_ttl_default,
        )

        # API modules
        self.users = UsersAPI(self._transport)
        self.blogs = BlogsAPI(self._transport)
        self.posts = PostsAPI(self._transport)
        self.comments = CommentsAPI(self._transport)
        self.subscriptions = SubscriptionsAPI(self._transport)
        self.donations = DonationsAPI(self._transport)
        self.targets = TargetsAPI(self._transport)
        self.showcase = ShowcaseAPI(self._transport)
        self.media = MediaAPI(self._transport)
        self.bundles = BundlesAPI(self._transport)

        # Events
        self._dispatcher = EventDispatcher()
        self._blog_username = blog_username
        self._poller = EventPoller(
            settings=self._settings,
            dispatcher=self._dispatcher,
            blog_username=blog_username,
            posts_api=self.posts,
            subscriptions_api=self.subscriptions,
            comments_api=self.comments,
        )

    def on(self, event_type: EventType) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register an event handler.

        Example::

            @client.on(EventType.NEW_DONATION)
            async def handle(event):
                print(event.amount)

        Args:
            event_type: EventType to listen for.

        Returns:
            Decorator registering the async event handler.
        """
        return self._dispatcher.on(event_type)

    async def start_polling(self, blog_username: str | None = None) -> None:
        """Start the event polling loop. Blocks until stopped.

        Args:
            blog_username: Override the blog to poll (if not set in constructor).
        """
        if blog_username:
            self._poller._blog = blog_username
        await self._poller.start()
        try:
            while self._poller._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self._poller.stop()

    async def stop_polling(self) -> None:
        """Stop the event polling loop."""
        await self._poller.stop()

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._poller.stop()
        await self._transport.close()

    async def __aenter__(self) -> Self:
        await self._auth_manager.initialize()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
