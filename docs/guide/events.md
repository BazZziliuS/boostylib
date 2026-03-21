# Event System

Since Boosty does not provide webhooks, boostylib uses a polling-based event system. The library periodically checks the API for changes and dispatches events to registered handlers.

## Registering Handlers

Use the `@client.on()` decorator:

```python
from boostylib import BoostyClient, EventType

client = BoostyClient(access_token="...")

@client.on(EventType.NEW_DONATION)
async def handle_donation(event):
    print(f"New donation: {event.amount} {event.currency} from {event.user.name}")

@client.on(EventType.NEW_SUBSCRIPTION)
async def handle_subscription(event):
    print(f"New subscriber: {event.user.name} at level {event.level.name}")

@client.on(EventType.SUBSCRIPTION_CANCELLED)
async def handle_cancel(event):
    print(f"Subscription cancelled: {event.user.name}")

@client.on(EventType.NEW_COMMENT)
async def handle_comment(event):
    print(f"New comment by {event.user.name}: {event.content}")
```

## Starting the Polling Loop

```python
async with client:
    await client.start_polling()
    # Runs until cancelled (Ctrl+C or client.stop_polling())
```

## Event Types

| Event Type | Event Model | Key Fields |
|---|---|---|
| `NEW_DONATION` | `DonationEvent` | `user`, `amount`, `currency`, `message`, `post_id` |
| `NEW_SUBSCRIPTION` | `SubscriptionEvent` | `user`, `level`, `welcome_post_id` |
| `SUBSCRIPTION_RENEWED` | `SubscriptionEvent` | `user`, `level` |
| `SUBSCRIPTION_CANCELLED` | `SubscriptionEvent` | `user`, `level` |
| `SUBSCRIPTION_LEVEL_CHANGED` | `SubscriptionEvent` | `user`, `level` |
| `NEW_COMMENT` | `CommentEvent` | `user`, `post_id`, `comment_id`, `content` |
| `NEW_POST` | `Event` | `blog_username`, `timestamp` |

## Multiple Handlers

You can register multiple handlers for the same event type:

```python
@client.on(EventType.NEW_DONATION)
async def log_donation(event):
    logger.info(f"Donation: {event.amount}")

@client.on(EventType.NEW_DONATION)
async def thank_donor(event):
    if event.amount >= 1000:
        await client.comments.create_comment(...)
```

Both handlers will be called in registration order. If one handler raises an exception, the others still execute.

## Programmatic Registration

```python
async def my_handler(event):
    ...

client._dispatcher.register(EventType.NEW_DONATION, my_handler)
```

## Polling Interval

Configure via settings:

```python
from boostylib import BoostySettings

settings = BoostySettings(poll_interval=60.0)  # poll every 60 seconds
client = BoostyClient(settings=settings, access_token="...")
```

Or via environment variable:

```bash
export BOOSTY_POLL_INTERVAL=60
```
