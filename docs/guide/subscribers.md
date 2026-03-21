# Subscriber Data

The subscribers endpoint returns rich data including **email addresses** and **payment history**.

## Get Subscribers

```python
subscribers = await client.subscriptions.get_subscribers("my_blog", limit=50)
for sub in subscribers:
    print(f"{sub.name}: {sub.email}, payments={sub.payments}")
```

## Async Iterator

```python
async for sub in client.subscriptions.iter_subscribers("my_blog"):
    if sub.is_paid:
        print(f"{sub.name}: {sub.email} — {sub.payments} RUB")
```

## Filter Paid Subscribers

```python
subs = await client.subscriptions.get_subscribers("my_blog", limit=100)
paid = [s for s in subs if s.is_paid and s.is_active]
print(f"Active paid subscribers: {len(paid)}")
```

## Subscriber Model

| Field | Type | Description |
|---|---|---|
| `id` | `int` | Boosty user ID |
| `name` | `str` | Display name |
| `email` | `str` | Email address |
| `avatar_url` | `str \| None` | Avatar URL |
| `level` | `SubscriptionLevel \| None` | Subscription tier |
| `price` | `int` | Subscription price |
| `payments` | `float` | Total lifetime payments (RUB) |
| `status` | `str` | `active` or `inactive` |
| `subscribed` | `bool` | Currently subscribed |
| `on_time` | `int \| None` | Subscribe timestamp (unix) |
| `off_time` | `int \| None` | Unsubscribe timestamp (unix) |
| `is_black_listed` | `bool` | Blacklisted |
| `can_write` | `bool` | Can send messages |

### Computed Properties

| Property | Description |
|---|---|
| `sub.is_active` | `status == "active" and subscribed` |
| `sub.is_paid` | `price > 0` |

## Integration Example: Export Paid Subscriber Emails

```python
async with BoostyClient(access_token="...") as client:
    emails = []
    async for sub in client.subscriptions.iter_subscribers("my_blog"):
        if sub.is_active and sub.payments > 0:
            emails.append(sub.email)

    # Write to file
    with open("paid_subscribers.txt", "w") as f:
        f.write("\n".join(emails))
```
