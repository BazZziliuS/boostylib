# Example: Auto-Responder

A standalone script that automatically responds to donations and new subscriptions.

## Dependencies

```bash
pip install boostylib
```

## Code

```python
import asyncio
import os

from boostylib import BoostyClient, EventType
from boostylib.auth import EnvTokenStorage

BLOG = os.environ["BOOSTY_BLOG"]

client = BoostyClient(token_storage=EnvTokenStorage())


@client.on(EventType.NEW_DONATION)
async def on_donation(event):
    """Thank donors based on amount."""
    if event.amount >= 5000:
        msg = f"INCREDIBLE! Thank you so much for {event.amount} {event.currency}, {event.user.name}! You're legendary!"
    elif event.amount >= 1000:
        msg = f"Wow, {event.user.name}! Thank you for {event.amount} {event.currency}! That's very generous!"
    elif event.amount >= 100:
        msg = f"Thank you for your support, {event.user.name}! Every bit helps!"
    else:
        return  # Skip very small donations

    if event.post_id:
        await client.comments.create_comment(event.blog_username, event.post_id, msg)


@client.on(EventType.NEW_SUBSCRIPTION)
async def on_subscription(event):
    """Welcome new subscribers."""
    msg = f"Welcome to {event.level.name}, {event.user.name}! Glad to have you here!"
    if event.welcome_post_id:
        await client.comments.create_comment(
            event.blog_username, event.welcome_post_id, msg
        )


@client.on(EventType.SUBSCRIPTION_CANCELLED)
async def on_cancel(event):
    """Log cancelled subscriptions."""
    print(f"[CANCEL] {event.user.name} cancelled {event.level.name}")


async def main():
    print(f"Starting auto-responder for {BLOG}...")
    async with client:
        await client.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables

```bash
export BOOSTY_BLOG=my_blog_username
export BOOSTY_ACCESS_TOKEN=...
export BOOSTY_REFRESH_TOKEN=...
export BOOSTY_DEVICE_ID=...
export BOOSTY_POLL_INTERVAL=30
```

## Running

```bash
python auto_responder.py
```

Press `Ctrl+C` to stop.
