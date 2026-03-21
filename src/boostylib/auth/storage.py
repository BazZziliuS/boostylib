"""Token storage implementations."""

from __future__ import annotations

import json
import logging
import os
import stat
import sys
from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import SecretStr

from boostylib.auth.models import TokenPair

logger = logging.getLogger("boostylib.auth")

_DEFAULT_AUTH_PATH = Path.home() / ".boosty" / "auth.json"


@runtime_checkable
class TokenStorage(Protocol):
    """Protocol for token persistence."""

    async def load(self) -> TokenPair | None: ...
    async def save(self, tokens: TokenPair) -> None: ...
    async def clear(self) -> None: ...


class MemoryTokenStorage:
    """In-memory token storage. Useful for tests and one-shot scripts."""

    def __init__(self) -> None:
        self._tokens: TokenPair | None = None

    async def load(self) -> TokenPair | None:
        return self._tokens

    async def save(self, tokens: TokenPair) -> None:
        self._tokens = tokens

    async def clear(self) -> None:
        self._tokens = None


class FileTokenStorage:
    """File-based token storage with secure permissions.

    Args:
        path: Path to the auth JSON file. Defaults to ``~/.boosty/auth.json``.
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _DEFAULT_AUTH_PATH

    async def load(self) -> TokenPair | None:
        if not self._path.exists():
            return None
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return TokenPair(
                access_token=SecretStr(data["access_token"]),
                refresh_token=SecretStr(data["refresh_token"]),
                device_id=data["device_id"],
                expires_at=data["expires_at"],
            )
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to load tokens from %s: %s", self._path, exc)
            return None

    async def save(self, tokens: TokenPair) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "access_token": tokens.access_token.get_secret_value(),
            "refresh_token": tokens.refresh_token.get_secret_value(),
            "device_id": tokens.device_id,
            "expires_at": tokens.expires_at,
        }
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._set_secure_permissions()

    async def clear(self) -> None:
        if self._path.exists():
            self._path.unlink()

    def _set_secure_permissions(self) -> None:
        """Set file permissions to owner-only (600 on Unix)."""
        if sys.platform == "win32":
            return  # Windows ACL handled separately
        try:
            self._path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        except OSError as exc:
            logger.warning("Could not set secure permissions on %s: %s", self._path, exc)


class EnvTokenStorage:
    """Read-only token storage from environment variables.

    Reads:
    - ``BOOSTY_ACCESS_TOKEN``
    - ``BOOSTY_REFRESH_TOKEN``
    - ``BOOSTY_DEVICE_ID``
    - ``BOOSTY_EXPIRES_AT`` (optional, defaults to 0)
    """

    async def load(self) -> TokenPair | None:
        access_token = os.environ.get("BOOSTY_ACCESS_TOKEN")
        refresh_token = os.environ.get("BOOSTY_REFRESH_TOKEN")
        device_id = os.environ.get("BOOSTY_DEVICE_ID")
        if not all([access_token, refresh_token, device_id]):
            return None
        return TokenPair(
            access_token=SecretStr(access_token),  # type: ignore[arg-type]
            refresh_token=SecretStr(refresh_token),  # type: ignore[arg-type]
            device_id=device_id,  # type: ignore[arg-type]
            expires_at=int(os.environ.get("BOOSTY_EXPIRES_AT", "0")),
        )

    async def save(self, tokens: TokenPair) -> None:
        logger.warning("EnvTokenStorage is read-only, cannot save tokens")

    async def clear(self) -> None:
        logger.warning("EnvTokenStorage is read-only, cannot clear tokens")
