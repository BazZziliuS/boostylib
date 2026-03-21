# Donation Tracking

Boosty does not have a dedicated donations endpoint. Donation data is available through:

- **Post objects**: `donations` (total amount) and `donators` (list of donors)
- **Subscriber objects**: `payments` (lifetime total of all payments)

## Get Donations for a Post

```python
info = await client.donations.get_post_donations("my_blog", "post_id")
print(f"Total: {info.total_amount}")
for donator in info.donators:
    print(f"  {donator}")
```

## Find All Posts with Donations

```python
async for info in client.donations.iter_posts_with_donations(
    "my_blog", posts_api=client.posts
):
    print(f"{info.post_title}: {info.total_amount} ({len(info.donators)} donators)")
```

## Get Paid Subscribers (Lifetime Payments)

```python
paid = await client.donations.get_paid_subscribers(
    "my_blog", subscriptions_api=client.subscriptions
)
for p in paid:
    print(f"{p.name} ({p.email}): {p.total_payments} RUB, active={p.is_active}")
```

## Subscriber Payments

The `Subscriber` model includes a `payments` field with the total lifetime payments:

```python
async for sub in client.subscriptions.iter_subscribers("my_blog"):
    if sub.payments > 0:
        print(f"{sub.name}: {sub.email} — {sub.payments} RUB")
```

See [Subscriber Data](subscribers.md) for the full model.
