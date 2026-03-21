"""Caching layer with pluggable backends."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CacheBackend(Protocol):
    """Protocol for cache storage backends."""

    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, *, ttl: int | None = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def clear(self) -> None: ...


class NullCache:
    """No-op cache — pass-through, nothing is stored."""

    async def get(self, key: str) -> bytes | None:
        return None

    async def set(self, key: str, value: bytes, *, ttl: int | None = None) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass

    async def clear(self) -> None:
        pass


class MemoryCache:
    """In-memory cache with TTL support.

    Stores cached values in a dict with expiration timestamps.
    Thread-safe via asyncio.Lock.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[bytes, float]] = {}  # key -> (value, expires_at)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> bytes | None:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at > 0 and time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: bytes, *, ttl: int | None = None) -> None:
        async with self._lock:
            expires_at = (time.monotonic() + ttl) if ttl and ttl > 0 else 0.0
            self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


class CacheManager:
    """High-level cache manager used by API modules.

    Provides typed get/set with automatic JSON serialization
    and configurable TTL per data type.
    """

    def __init__(
        self,
        backend: CacheBackend | None = None,
        *,
        enabled: bool = True,
        ttl_blog: int = 300,
        ttl_levels: int = 600,
        ttl_user: int = 120,
        ttl_default: int = 60,
    ) -> None:
        self._backend: CacheBackend = backend or (MemoryCache() if enabled else NullCache())
        self.enabled = enabled
        self.ttl_blog = ttl_blog
        self.ttl_levels = ttl_levels
        self.ttl_user = ttl_user
        self.ttl_default = ttl_default

    async def get_json(self, key: str) -> Any | None:
        """Get a cached JSON value."""
        if not self.enabled:
            return None
        data = await self._backend.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set_json(self, key: str, value: Any, *, ttl: int | None = None) -> None:
        """Cache a JSON-serializable value."""
        if not self.enabled:
            return
        await self._backend.set(key, json.dumps(value).encode(), ttl=ttl or self.ttl_default)

    async def delete(self, key: str) -> None:
        """Delete a cached entry."""
        await self._backend.delete(key)

    async def invalidate_pattern(self, prefix: str) -> None:
        """Invalidate all keys starting with prefix (MemoryCache only)."""
        if isinstance(self._backend, MemoryCache):
            async with self._backend._lock:
                keys_to_delete = [k for k in self._backend._store if k.startswith(prefix)]
                for k in keys_to_delete:
                    del self._backend._store[k]

    async def clear(self) -> None:
        """Clear all cached data."""
        await self._backend.clear()
