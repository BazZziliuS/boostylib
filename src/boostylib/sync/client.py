"""Synchronous wrapper over async BoostyClient."""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Self

from boostylib.auth.models import AuthCredentials
from boostylib.auth.storage import TokenStorage
from boostylib.config import BoostySettings
from boostylib.sync._wrapper import SyncProxy


class SyncBoostyClient:
    """Synchronous wrapper for BoostyClient.

    Runs an asyncio event loop in a background thread and proxies
    all API calls synchronously.

    Example::

        with SyncBoostyClient(access_token="...") as client:
            user = client.users.get_current_user()
            print(user.name)
    """

    def __init__(
        self,
        *,
        access_token: str | None = None,
        credentials: AuthCredentials | None = None,
        token_storage: TokenStorage | None = None,
        settings: BoostySettings | None = None,
        middleware: list[Any] | None = None,
    ) -> None:
        from boostylib.client import BoostyClient

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

        self._async_client = BoostyClient(
            access_token=access_token,
            credentials=credentials,
            token_storage=token_storage,
            settings=settings,
            middleware=middleware,
        )

        # Initialize auth
        self._run(self._async_client._auth_manager.initialize())

        # Create sync proxies for all API modules
        self.users = SyncProxy(self._async_client.users, self._run)
        self.blogs = SyncProxy(self._async_client.blogs, self._run)
        self.posts = SyncProxy(self._async_client.posts, self._run)
        self.comments = SyncProxy(self._async_client.comments, self._run)
        self.subscriptions = SyncProxy(self._async_client.subscriptions, self._run)
        self.donations = SyncProxy(self._async_client.donations, self._run)
        self.targets = SyncProxy(self._async_client.targets, self._run)
        self.showcase = SyncProxy(self._async_client.showcase, self._run)
        self.media = SyncProxy(self._async_client.media, self._run)
        self.bundles = SyncProxy(self._async_client.bundles, self._run)

    def _run(self, coro: Any) -> Any:
        """Run a coroutine on the background loop and return the result."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def close(self) -> None:
        """Close the client and stop the background event loop."""
        self._run(self._async_client.close())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        self._loop.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
