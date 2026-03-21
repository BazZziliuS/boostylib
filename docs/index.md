# boostylib

**Async Python library for the [Boosty.to](https://boosty.to) API.**

Manage subscriptions, posts, donations, and automate responses — all from Python 3.14+.

## Highlights

- Fully async (`async`/`await`) with `httpx` + synchronous wrapper
- Automatic token refresh with pluggable storage
- Pydantic v2 models — including **subscriber emails and payments**
- Fluent `PostBuilder` with access control (subscription levels, donations)
- Subscription level and target/goal CRUD
- Decorator-based event system with real polling detectors
- In-memory caching with TTL and pluggable backends
- Media uploads, pagination, middleware, rate limiting
- PEP 561 typed — full `mypy --strict` support

## Quick Examples

### Async

```python
from boostylib import BoostyClient

async with BoostyClient(access_token="...") as client:
    # Get subscriber emails
    async for sub in client.subscriptions.iter_subscribers("my_blog"):
        print(f"{sub.name}: {sub.email}, paid={sub.payments}")

    # Create a post
    from boostylib.builders import PostBuilder
    post = PostBuilder().title("Hello").text("World").free().build()
    await client.posts.create_post("my_blog", post)
```

### Sync

```python
from boostylib.sync import SyncBoostyClient

with SyncBoostyClient(access_token="...") as client:
    user = client.users.get_current_user()
    print(user.name)
```

### Auto-respond to events

```python
from boostylib import BoostyClient, EventType

client = BoostyClient(access_token="...", blog_username="my_blog")

@client.on(EventType.NEW_COMMENT)
async def reply(event):
    await client.comments.create_comment(
        event.blog_username, event.post_id,
        f"Thanks, {event.user.name}!",
    )

async with client:
    await client.start_polling()
```

## Getting Started

1. [Installation](getting-started/installation.md) — Install with pip or uv
2. [Authentication](getting-started/authentication.md) — Get your Boosty tokens
3. [Quick Start](getting-started/quickstart.md) — Your first API call in 5 minutes

## Links

- [GitHub Repository](https://github.com/BazZziliuS/boostylib)
- [PyPI](https://pypi.org/project/boostylib/)
- [Changelog](changelog.md)
