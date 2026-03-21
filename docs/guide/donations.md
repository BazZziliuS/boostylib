# Donation Tracking

## List Donations

```python
page = await client.donations.get_donations("my_blog", limit=20)
for donation in page.data:
    print(f"{donation.user.name}: {donation.amount} {donation.currency}")
    if donation.message:
        print(f"  Message: {donation.message}")
```

### Filter by Date

```python
# Unix timestamps
page = await client.donations.get_donations(
    "my_blog",
    from_ts=1700000000,
    to_ts=1710000000,
)
```

### Async Iterator

```python
async for donation in client.donations.iter_donations("my_blog"):
    print(f"{donation.user.name}: {donation.amount}")
```

## Auto-Respond to Donations

See [Event System](events.md) for the full decorator-based approach.

```python
from boostylib import EventType

@client.on(EventType.NEW_DONATION)
async def thank_donor(event):
    if event.amount >= 500:
        await client.comments.create_comment(
            event.blog_username,
            event.post_id,
            f"Thank you for {event.amount} {event.currency}, {event.user.name}!",
        )
```
