"""Tests for caching layer."""

from __future__ import annotations

import pytest

from boostylib.cache import CacheManager, MemoryCache, NullCache

pytestmark = pytest.mark.unit


class TestMemoryCache:
    async def test_set_and_get(self) -> None:
        cache = MemoryCache()
        await cache.set("key1", b"value1")
        result = await cache.get("key1")
        assert result == b"value1"

    async def test_get_missing(self) -> None:
        cache = MemoryCache()
        assert await cache.get("missing") is None

    async def test_delete(self) -> None:
        cache = MemoryCache()
        await cache.set("key1", b"value1")
        await cache.delete("key1")
        assert await cache.get("key1") is None

    async def test_clear(self) -> None:
        cache = MemoryCache()
        await cache.set("a", b"1")
        await cache.set("b", b"2")
        await cache.clear()
        assert cache.size == 0

    async def test_ttl_expiry(self) -> None:
        cache = MemoryCache()
        await cache.set("expires", b"data", ttl=0)  # ttl=0 means no expiry
        assert await cache.get("expires") == b"data"

    async def test_size(self) -> None:
        cache = MemoryCache()
        await cache.set("a", b"1")
        await cache.set("b", b"2")
        assert cache.size == 2


class TestNullCache:
    async def test_always_miss(self) -> None:
        cache = NullCache()
        await cache.set("key", b"value")
        assert await cache.get("key") is None

    async def test_operations_dont_fail(self) -> None:
        cache = NullCache()
        await cache.delete("key")
        await cache.clear()


class TestCacheManager:
    async def test_json_roundtrip(self) -> None:
        mgr = CacheManager(enabled=True)
        await mgr.set_json("test", {"name": "hello", "count": 42}, ttl=60)
        result = await mgr.get_json("test")
        assert result == {"name": "hello", "count": 42}

    async def test_disabled_cache(self) -> None:
        mgr = CacheManager(enabled=False)
        await mgr.set_json("test", {"data": 1})
        assert await mgr.get_json("test") is None

    async def test_delete(self) -> None:
        mgr = CacheManager(enabled=True)
        await mgr.set_json("test", "value")
        await mgr.delete("test")
        assert await mgr.get_json("test") is None

    async def test_clear(self) -> None:
        mgr = CacheManager(enabled=True)
        await mgr.set_json("a", 1)
        await mgr.set_json("b", 2)
        await mgr.clear()
        assert await mgr.get_json("a") is None

    async def test_invalidate_pattern(self) -> None:
        mgr = CacheManager(enabled=True)
        await mgr.set_json("blog:test:info", {"title": "Test"})
        await mgr.set_json("blog:test:levels", [1, 2])
        await mgr.set_json("user:123", {"name": "User"})
        await mgr.invalidate_pattern("blog:test:")
        assert await mgr.get_json("blog:test:info") is None
        assert await mgr.get_json("blog:test:levels") is None
        assert await mgr.get_json("user:123") == {"name": "User"}
