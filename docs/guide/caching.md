# Caching

boostylib includes a built-in caching layer to reduce API calls for data that changes infrequently.

## Default Behavior

Cache is **enabled by default** using `MemoryCache` (in-process, with TTL):

```python
from boostylib import BoostyClient

client = BoostyClient(access_token="...")
# Cache is active — repeated calls to get_blog(), get_levels() etc. are fast
```

## Disable Cache

```python
from boostylib import BoostyClient, BoostySettings

client = BoostyClient(
    access_token="...",
    settings=BoostySettings(cache_enabled=False),
)
```

## TTL Configuration

| Setting | Default | Description |
|---|---|---|
| `cache_ttl_blog` | 300s (5 min) | Blog info |
| `cache_ttl_levels` | 600s (10 min) | Subscription levels |
| `cache_ttl_user` | 120s (2 min) | User profile |
| `cache_ttl_default` | 60s (1 min) | Everything else |

```python
settings = BoostySettings(
    cache_ttl_blog=600,      # 10 minutes
    cache_ttl_levels=1800,   # 30 minutes
    cache_ttl_default=30,    # 30 seconds
)
```

## Manual Cache Operations

```python
# Clear everything
await client.cache.clear()

# Delete a specific key
await client.cache.delete("blog:my_blog:info")

# Invalidate all keys with a prefix
await client.cache.invalidate_pattern("blog:my_blog:")

# Direct JSON get/set
await client.cache.set_json("my_key", {"data": 42}, ttl=120)
value = await client.cache.get_json("my_key")
```

## Custom Cache Backend

Implement the `CacheBackend` protocol:

```python
from boostylib.cache import CacheBackend

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = ...  # your Redis client

    async def get(self, key: str) -> bytes | None:
        return await self.redis.get(f"boosty:{key}")

    async def set(self, key: str, value: bytes, *, ttl: int | None = None) -> None:
        await self.redis.set(f"boosty:{key}", value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(f"boosty:{key}")

    async def clear(self) -> None:
        keys = await self.redis.keys("boosty:*")
        if keys:
            await self.redis.delete(*keys)

# Use it
client = BoostyClient(access_token="...", cache=RedisCache("redis://localhost"))
```

## Built-in Backends

| Backend | Description |
|---|---|
| `MemoryCache` | In-memory dict with TTL (default when enabled) |
| `NullCache` | No-op — nothing is cached (default when disabled) |
