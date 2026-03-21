"""Auth manager: token lifecycle, auto-refresh, thread-safety."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING

import httpx
from pydantic import SecretStr

from boostylib.auth.models import AuthCredentials, TokenPair
from boostylib.auth.storage import MemoryTokenStorage, TokenStorage
from boostylib.http.exceptions import BoostyAuthError

if TYPE_CHECKING:
    from boostylib.config import BoostySettings

logger = logging.getLogger("boostylib.auth")

_TOKEN_REFRESH_URL = "https://api.boosty.to/oauth/token/"


class AuthManager:
    """Manages authentication tokens with auto-refresh.

    Args:
        settings: Boosty settings for refresh margin and timeouts.
        token_storage: Storage backend for token persistence.
        credentials: Initial credentials (optional, loaded from storage if not given).
        access_token: Shortcut for static access token (no refresh).
    """

    def __init__(
        self,
        *,
        settings: BoostySettings,
        token_storage: TokenStorage | None = None,
        credentials: AuthCredentials | None = None,
        access_token: str | None = None,
    ) -> None:
        self._settings = settings
        self._storage = token_storage or MemoryTokenStorage()
        self._tokens: TokenPair | None = None
        self._lock = asyncio.Lock()
        self._initial_credentials = credentials
        self._static_token = access_token

    async def initialize(self) -> None:
        """Load tokens from storage or initial credentials."""
        if self._static_token:
            self._tokens = TokenPair(
                access_token=SecretStr(self._static_token),
                refresh_token=SecretStr(""),
                device_id="",
                expires_at=0,
            )
            return

        if self._initial_credentials:
            self._tokens = TokenPair(
                access_token=self._initial_credentials.access_token,
                refresh_token=self._initial_credentials.refresh_token,
                device_id=self._initial_credentials.device_id,
                expires_at=self._initial_credentials.expires_at,
            )
            await self._storage.save(self._tokens)
            return

        self._tokens = await self._storage.load()

    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if needed.

        Returns:
            Access token string.

        Raises:
            BoostyAuthError: If no tokens are available.
        """
        async with self._lock:
            if self._tokens is None:
                raise BoostyAuthError("No tokens available. Call initialize() first.")

            # Static token — never refresh
            if self._static_token:
                return self._tokens.access_token.get_secret_value()

            # Check if refresh is needed
            if self._is_expiring_soon():
                await self._do_refresh()

            return self._tokens.access_token.get_secret_value()

    async def refresh(self) -> bool:
        """Force a token refresh.

        Returns:
            True if refresh succeeded, False otherwise.
        """
        async with self._lock:
            return await self._do_refresh()

    def _is_expiring_soon(self) -> bool:
        if self._tokens is None or self._tokens.expires_at == 0:
            return False
        return time.time() >= (self._tokens.expires_at - self._settings.token_refresh_margin)

    async def _do_refresh(self) -> bool:
        if self._tokens is None:
            return False

        refresh_token = self._tokens.refresh_token.get_secret_value()
        if not refresh_token:
            logger.warning("No refresh token available")
            return False

        logger.info("Refreshing access token")

        try:
            async with httpx.AsyncClient(timeout=self._settings.timeout) as client:
                response = await client.post(
                    _TOKEN_REFRESH_URL,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "device_id": self._tokens.device_id,
                        "device_os": "web",
                    },
                )

            if response.status_code != 200:
                logger.error("Token refresh failed: %d %s", response.status_code, response.text)
                return False

            data = response.json()
            self._tokens = TokenPair(
                access_token=SecretStr(data["access_token"]),
                refresh_token=SecretStr(data.get("refresh_token", refresh_token)),
                device_id=self._tokens.device_id,
                expires_at=data.get("expires_at", 0),
            )
            await self._storage.save(self._tokens)
            logger.info("Token refreshed successfully, expires_at=%d", self._tokens.expires_at)
            return True

        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.error("Token refresh error: %s", exc)
            return False
