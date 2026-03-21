# Quick Start

This guide gets you from zero to your first API call in under 5 minutes.

## 1. Install

```bash
pip install boostylib
```

## 2. Get Your Token

See [Authentication](authentication.md) for detailed instructions. For a quick test, grab your `access_token` from browser DevTools.

## 3. Read Your Profile

```python
import asyncio
from boostylib import BoostyClient

async def main():
    async with BoostyClient(access_token="your_token") as client:
        user = await client.users.get_current_user()
        print(f"Logged in as: {user.name} (id={user.id})")

asyncio.run(main())
```

## 4. List Your Blog's Posts

```python
async def main():
    async with BoostyClient(access_token="your_token") as client:
        page = await client.posts.list_posts("your_blog_username", limit=5)
        for post in page.data:
            print(f"[{post.id}] {post.title}")

asyncio.run(main())
```

## 5. Check a Subscription

```python
async def main():
    async with BoostyClient(access_token="your_token") as client:
        status = await client.subscriptions.verify_subscription(
            "your_blog_username", "target_user_id"
        )
        if status.is_subscribed:
            print(f"Subscribed at level: {status.level.name}")
        else:
            print("Not subscribed")

asyncio.run(main())
```

## 6. Create a Post

```python
from boostylib.builders import PostBuilder

async def main():
    async with BoostyClient(access_token="your_token") as client:
        post = (
            PostBuilder()
            .title("Hello from boostylib!")
            .text("This post was created programmatically.")
            .free()
            .tags(["test", "api"])
            .build()
        )
        created = await client.posts.create_post("your_blog_username", post)
        print(f"Created post: {created.id}")

asyncio.run(main())
```

## Next Steps

- [Configuration](../guide/configuration.md) — Customize timeouts, retries, rate limits
- [Working with Posts](../guide/posts.md) — PostBuilder, access levels, file uploads
- [Event System](../guide/events.md) — Auto-respond to donations and subscriptions
