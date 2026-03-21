# boostylib

[![PyPI](https://img.shields.io/pypi/v/boostylib)](https://pypi.org/project/boostylib/)
[![Python](https://img.shields.io/pypi/pyversions/boostylib)](https://pypi.org/project/boostylib/)
[![Tests](https://img.shields.io/github/actions/workflow/status/BazZziliuS/boostylib/ci.yml?label=tests)](https://github.com/BazZziliuS/boostylib/actions)
[![License](https://img.shields.io/pypi/l/boostylib)](LICENSE)

Async Python library for the [Boosty.to](https://boosty.to) API. Manage subscriptions, posts, donations, and automate responses — all from Python.

---

## Features

- Fully async (`async`/`await`) with `httpx` + **synchronous wrapper** (`SyncBoostyClient`)
- Automatic token refresh with pluggable storage backends
- Pydantic v2 models with strict validation
- **Subscriber data with email, payments, and status**
- Fluent `PostBuilder` for creating posts with access control (subscription levels, donations)
- Two-step post creation (draft → publish) matching Boosty's real API flow
- Subscription level CRUD (create, list, delete)
- Target/goal management (money and subscriber goals)
- Decorator-based event system with **real polling detectors** for new subscribers, comments, and cancellations
- Auto-reply to comments with threading support
- Media uploads (images, files, video, audio)
- **In-memory caching** with TTL and pluggable backends (`CacheBackend` protocol)
- Configurable retry with exponential backoff and rate limiting
- Middleware pipeline for custom request/response processing
- Browser-like HTTP fingerprint for write operations
- PEP 561 typed — full `mypy --strict` support

## Installation

```bash
pip install boostylib
```

or with [uv](https://docs.astral.sh/uv/):

```bash
uv add boostylib
```

## Quick Start

### Getting Your Tokens

1. Log in to [boosty.to](https://boosty.to)
2. Open DevTools (`F12`) → Application → Local Storage → `https://boosty.to`
3. Copy the `auth` object (`access_token`, `refresh_token`, `expires_at`) and `_clentId` (this is the `device_id`)

### Verify a Subscription

```python
from boostylib import BoostyClient

async with BoostyClient(access_token="your_token") as client:
    status = await client.subscriptions.verify_subscription("my_blog", "user_id")

    if status.is_subscribed:
        print(f"Subscribed: {status.level.name} (paid={status.is_paid})")
    else:
        print("Not subscribed")
```

### Get Subscriber Emails and Payments

```python
async with BoostyClient(access_token="...") as client:
    subscribers = await client.subscriptions.get_subscribers("my_blog")
    for sub in subscribers:
        print(f"{sub.name}: {sub.email}, payments={sub.payments}, active={sub.is_active}")

    # Async iterator for all subscribers
    async for sub in client.subscriptions.iter_subscribers("my_blog"):
        if sub.is_paid:
            print(f"Paid: {sub.name} ({sub.email}) — {sub.payments} RUB")
```

### Create a Post for Premium Subscribers

```python
from boostylib import BoostyClient, AuthCredentials
from boostylib.builders import PostBuilder

creds = AuthCredentials(
    access_token="...",
    refresh_token="...",
    device_id="...",
)

async with BoostyClient(credentials=creds) as client:
    levels = await client.subscriptions.get_levels("my_blog")
    premium = next(l for l in levels if l.name == "Premium")

    post = (
        PostBuilder()
        .title("Premium Only Content")
        .text("This is exclusive content for premium subscribers.")
        .image(url="https://example.com/img.png")
        .access_level(level_id=str(premium.id))
        .teaser("Subscribe to Premium to unlock this post!")
        .build()
    )

    created = await client.posts.create_post("my_blog", post)
    print(f"Post created: {created.id}")
```

### Create a Post Unlocked by Donation

```python
from boostylib.builders import PostBuilder

post = (
    PostBuilder()
    .title("Exclusive for Donors")
    .text("Available to anyone who donated 500+ RUB")
    .minimum_donation(amount=500, currency="RUB")
    .build()
)
```

### Auto-Respond to Events

```python
from boostylib import BoostyClient, EventType

client = BoostyClient(access_token="...", blog_username="my_blog")

@client.on(EventType.NEW_SUBSCRIPTION)
async def on_subscribe(event):
    await client.comments.create_comment(
        event.blog_username,
        event.welcome_post_id,
        f"Welcome to {event.level.name}, {event.user.name}!",
    )

@client.on(EventType.NEW_COMMENT)
async def on_comment(event):
    await client.comments.create_comment(
        event.blog_username, event.post_id,
        f"Thanks for commenting, {event.user.name}!",
        reply_to=str(event.comment_id),
    )

@client.on(EventType.SUBSCRIPTION_CANCELLED)
async def on_cancel(event):
    print(f"Lost subscriber: {event.user.name}")

async with client:
    await client.start_polling()
```

### Synchronous Usage

No `async`/`await` needed — works in scripts, Django views, Jupyter notebooks:

```python
from boostylib.sync import SyncBoostyClient

with SyncBoostyClient(access_token="...") as client:
    user = client.users.get_current_user()
    print(user.name)

    subscribers = client.subscriptions.get_subscribers("my_blog")
    for sub in subscribers:
        print(f"{sub.name}: {sub.email}")

    post = PostBuilder().title("Hello").text("World").free().build()
    client.posts.create_post("my_blog", post)
```

### Upload a File

```python
from pathlib import Path
from boostylib import BoostyClient
from boostylib.builders import PostBuilder

async with BoostyClient(access_token="...") as client:
    media = await client.media.upload_file(
        Path("./project_source.zip"),
        filename="project_source.zip",
    )

    post = (
        PostBuilder()
        .title("Project Sources")
        .text("Download the full source archive:")
        .file(media_id=media.id, filename=media.filename)
        .access_level(level_id="premium_level_id")
        .build()
    )
    await client.posts.create_post("my_blog", post)
```

### Manage Subscription Levels

```python
async with BoostyClient(access_token="...") as client:
    # Create a level
    level = await client.subscriptions.create_level(
        "my_blog", name="VIP", price=1000, description="Exclusive access"
    )
    print(f"Created: {level.name} (id={level.id})")

    # Delete a level
    await client.subscriptions.delete_level("my_blog", level.id)
```

### Manage Goals/Targets

```python
from boostylib.enums import TargetType

async with BoostyClient(access_token="...") as client:
    # Money goal
    goal = await client.targets.create_target(
        "my_blog", description="New equipment", target_sum=50000, target_type=TargetType.MONEY,
    )

    # Subscriber goal
    sub_goal = await client.targets.create_target(
        "my_blog", description="1000 subscribers!", target_sum=1000, target_type=TargetType.SUBSCRIBERS,
    )

    # Read back
    fetched = await client.targets.get_target(goal.id)
    print(f"{fetched.description}: {fetched.current_sum}/{fetched.target_sum}")

    # Clean up
    await client.targets.delete_target(goal.id)
```

## Configuration

All settings can be configured via environment variables, a TOML file, or programmatically.

### Environment Variables

```bash
export BOOSTY_ACCESS_TOKEN=...
export BOOSTY_REFRESH_TOKEN=...
export BOOSTY_DEVICE_ID=...
export BOOSTY_TIMEOUT=30
export BOOSTY_MAX_RETRIES=3
export BOOSTY_POLL_INTERVAL=60
export BOOSTY_DEBUG=true
export BOOSTY_CACHE_ENABLED=true
```

### TOML Config (`boosty.toml`)

```toml
timeout = 30.0
max_retries = 3
poll_interval = 60.0
rate_limit_requests = 60
cache_enabled = true
cache_ttl_blog = 300
cache_ttl_levels = 600
debug = false
```

### Programmatic

```python
from boostylib import BoostyClient, BoostySettings

settings = BoostySettings(timeout=10.0, max_retries=5, debug=True)
client = BoostyClient(settings=settings, access_token="...")
```

## Caching

Built-in in-memory cache with configurable TTL:

```python
from boostylib import BoostyClient, BoostySettings

# Cache enabled by default (MemoryCache)
client = BoostyClient(access_token="...")

# Disable cache
client = BoostyClient(access_token="...", settings=BoostySettings(cache_enabled=False))

# Manual cache operations
await client.cache.clear()
await client.cache.delete("blog:my_blog:info")
await client.cache.invalidate_pattern("blog:my_blog:")
```

Custom cache backend (e.g. Redis):

```python
from boostylib.cache import CacheBackend

class RedisCache:
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, *, ttl: int | None = None) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def clear(self) -> None: ...

client = BoostyClient(access_token="...", cache=RedisCache())
```

## Token Storage

| Backend | Description |
|---|---|
| `MemoryTokenStorage` | In-memory, for tests and one-shot scripts (default) |
| `FileTokenStorage` | Persists to `~/.boosty/auth.json` with secure file permissions |
| `EnvTokenStorage` | Reads from `BOOSTY_*` environment variables (read-only) |

Custom storage:

```python
from boostylib.auth.storage import TokenStorage, TokenPair

class RedisTokenStorage:
    async def load(self) -> TokenPair | None: ...
    async def save(self, tokens: TokenPair) -> None: ...
    async def clear(self) -> None: ...
```

## Middleware

```python
from boostylib import BoostyClient
from boostylib.http.middleware import BaseMiddleware
import httpx

class LoggingMiddleware(BaseMiddleware):
    async def on_request(self, request: httpx.Request) -> httpx.Request:
        print(f"-> {request.method} {request.url}")
        return request

    async def on_response(self, response: httpx.Response) -> httpx.Response:
        print(f"<- {response.status_code}")
        return response

client = BoostyClient(access_token="...", middleware=[LoggingMiddleware()])
```

## API Reference

### Client

| Property / Method | Description |
|---|---|
| `client.users` | Current user info |
| `client.blogs` | Blog info, blacklist |
| `client.posts` | CRUD posts (draft → publish flow), list with filters |
| `client.comments` | Read, create, delete, reply to comments |
| `client.subscriptions` | Levels CRUD, verification, subscribers with email/payments |
| `client.donations` | Donation data from posts and subscriber payments |
| `client.targets` | CRUD goals (money and subscriber targets) |
| `client.showcase` | Showcase items |
| `client.media` | Upload images, files, video, audio |
| `client.bundles` | Bundle management |
| `client.cache` | Cache manager (get, set, clear, invalidate) |
| `client.on(EventType)` | Decorator to register event handlers |
| `client.start_polling(blog)` | Start event polling loop |
| `client.stop_polling()` | Stop polling |

### Subscriber Model

| Field | Type | Description |
|---|---|---|
| `id` | `int` | User ID |
| `name` | `str` | Display name |
| `email` | `str` | Email address |
| `level` | `SubscriptionLevel` | Subscription tier |
| `price` | `int` | Subscription price |
| `payments` | `float` | Total payments made |
| `status` | `str` | `active` / `inactive` |
| `subscribed` | `bool` | Currently subscribed |
| `on_time` | `int` | Subscribe timestamp |
| `off_time` | `int` | Unsubscribe timestamp |
| `is_active` | `bool` | Property: active + subscribed |
| `is_paid` | `bool` | Property: price > 0 |
| `can_write` | `bool` | Can send messages |

### PostBuilder

| Method | Description |
|---|---|
| `.title(str)` | Set post title |
| `.text(str)` | Add text block |
| `.image(url=..., media_id=...)` | Add image block |
| `.video(url=..., media_id=...)` | Add video block |
| `.audio(url=..., media_id=...)` | Add audio block |
| `.file(media_id=..., filename=...)` | Add file block |
| `.link(url=..., title=...)` | Add link block |
| `.free()` | Free for everyone |
| `.access_level(level_id=...)` | Restrict to subscription level |
| `.minimum_donation(amount, currency)` | Restrict to donors |
| `.subscribers_only()` | Any paid subscriber |
| `.teaser(str)` | Preview for non-subscribers |
| `.tags(list)` | Set tags |
| `.scheduled_at(datetime)` | Schedule for later |
| `.build()` | Build `PostCreateRequest` |

### Event Types

| Event | Detected by | Description |
|---|---|---|
| `NEW_SUBSCRIPTION` | Polling | New subscriber appeared |
| `SUBSCRIPTION_CANCELLED` | Polling | Subscriber disappeared from list |
| `NEW_COMMENT` | Polling | New comment on recent posts |
| `NEW_DONATION` | Polling | New donation (via subscriber payments diff) |
| `SUBSCRIPTION_RENEWED` | — | Subscription renewed |
| `SUBSCRIPTION_LEVEL_CHANGED` | — | Subscription tier changed |
| `NEW_POST` | — | New post published |

### Exceptions

| Exception | Status | Description |
|---|---|---|
| `BoostyError` | — | Base exception |
| `BoostyAuthError` | 401 | Invalid/expired token |
| `BoostyForbiddenError` | 403 | Insufficient permissions |
| `BoostyNotFoundError` | 404 | Resource not found |
| `BoostyRateLimitError` | 429 | Rate limit exceeded |
| `BoostyServerError` | 5xx | Server-side error |
| `BoostyNetworkError` | — | Connection/timeout errors |

## Pagination

```python
# Manual pagination
page = await client.posts.list_posts("blog", limit=10)
for post in page.data:
    print(post.title)
# Next page: page.cursor, page.is_last

# Async iterator (auto-pagination)
async for post in client.posts.iter_posts("blog"):
    print(post.title)
```

Available iterators: `iter_posts()`, `iter_donations()`, `iter_comments()`, `iter_subscribers()`.

## Development

```bash
# Clone
git clone https://github.com/BazZziliuS/boostylib.git
cd boostylib

# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest -m "unit or integration" -v   # no API access needed
uv run pytest -m e2e -v -s                   # requires .env with credentials

# Lint & format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run mypy src/

# Build
uv build
```

## Disclaimer

This library interacts with Boosty.to's **unofficial, reverse-engineered API**. Endpoints may change without notice. Use at your own risk and in accordance with Boosty's Terms of Service. This project is intended for personal and research use.

## License

[MIT](LICENSE)
