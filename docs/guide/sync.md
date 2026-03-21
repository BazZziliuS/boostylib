# Synchronous Client

`SyncBoostyClient` wraps the async client for use in synchronous code — scripts, Django views, Jupyter notebooks, CLI tools.

## Usage

```python
from boostylib.sync import SyncBoostyClient

with SyncBoostyClient(access_token="...") as client:
    user = client.users.get_current_user()
    print(f"Logged in as: {user.name}")

    # All API modules work the same way
    subscribers = client.subscriptions.get_subscribers("my_blog")
    for sub in subscribers:
        print(f"{sub.name}: {sub.email}")
```

## How It Works

`SyncBoostyClient` runs an `asyncio.EventLoop` in a background daemon thread. Each method call dispatches the coroutine to that loop and blocks until the result is ready. This means:

- All API modules (`users`, `posts`, `comments`, etc.) are available
- Methods have the same signatures as the async versions (minus `await`)
- Context manager (`with`) handles initialization and cleanup
- Thread-safe — the background loop is dedicated

## Creating Posts

```python
from boostylib.sync import SyncBoostyClient
from boostylib.builders import PostBuilder

with SyncBoostyClient(access_token="...") as client:
    post = (
        PostBuilder()
        .title("Posted from sync code")
        .text("No async/await needed!")
        .free()
        .build()
    )
    created = client.posts.create_post("my_blog", post)
    print(f"Created: {created.id}")
```

## With Credentials (auto-refresh)

```python
from boostylib import AuthCredentials
from boostylib.sync import SyncBoostyClient

creds = AuthCredentials(
    access_token="...",
    refresh_token="...",
    device_id="...",
)

with SyncBoostyClient(credentials=creds) as client:
    blog = client.blogs.get_blog("my_blog")
    print(f"Blog: {blog.title}, Posts: {blog.post_count}")
```

## Limitations

- Async iterators (`iter_posts`, `iter_subscribers`) are not available in sync mode — use the paginated `get_*` methods instead
- Event polling (`start_polling`) is not supported — use the async client for long-running event listeners
- Slightly higher overhead than async due to thread synchronization
