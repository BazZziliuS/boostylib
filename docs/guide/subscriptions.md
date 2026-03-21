# Subscription Verification

## Get Subscription Levels

```python
levels = await client.subscriptions.get_levels("my_blog")
for level in levels:
    print(f"{level.name}: {level.price} {level.currency} (free={level.is_free})")
```

## Verify a User's Subscription

```python
status = await client.subscriptions.verify_subscription("my_blog", "user_id")

if status.is_subscribed:
    print(f"Level: {status.level.name}")
    print(f"Paid: {status.is_paid}")
    print(f"Price: {status.price} {status.currency}")
else:
    print("Not subscribed")
```

### SubscriptionStatus Fields

| Field | Type | Description |
|---|---|---|
| `is_subscribed` | `bool` | Whether the user has an active subscription |
| `level` | `SubscriptionLevel \| None` | The subscription level (if subscribed) |
| `expires_at` | `datetime \| None` | When the subscription expires |
| `is_paid` | `bool` | Whether this is a paid (non-free) subscription |
| `price` | `int \| None` | Level price |
| `currency` | `str \| None` | Price currency |

## List Subscribers

```python
# All subscribers
data = await client.subscriptions.get_subscribers("my_blog", limit=50)

# Filter by level
data = await client.subscriptions.get_subscribers("my_blog", level_id=123)
```

### Async Iterator

```python
async for subscriber in client.subscriptions.iter_subscribers("my_blog"):
    print(subscriber)
```

## Integration Example: Telegram Bot

```python
from aiogram import Router
from aiogram.filters import Command
from boostylib import BoostyClient

router = Router()
boosty = BoostyClient(access_token="...")

@router.message(Command("check"))
async def check_sub(message):
    boosty_id = await db.get_boosty_id(message.from_user.id)
    if not boosty_id:
        await message.answer("Link your Boosty account first: /link")
        return

    status = await boosty.subscriptions.verify_subscription("my_blog", boosty_id)
    if status.is_subscribed and status.is_paid:
        await message.answer(f"Active: {status.level.name}")
    else:
        await message.answer("No active subscription")
```
