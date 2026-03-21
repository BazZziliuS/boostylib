# Working with Posts

## Listing Posts

```python
page = await client.posts.list_posts("my_blog", limit=10)
for post in page.data:
    print(f"{post.id}: {post.title}")
```

### Filtering

```python
# By subscription level
page = await client.posts.list_posts("my_blog", level_id="premium_id")

# By date range (unix timestamps)
page = await client.posts.list_posts("my_blog", from_ts=1700000000, to_ts=1710000000)

# By tags
page = await client.posts.list_posts("my_blog", tags_ids=["devlog", "update"])
```

### Async Iterator

```python
async for post in client.posts.iter_posts("my_blog"):
    print(post.title)
```

## Getting a Single Post

```python
post = await client.posts.get_post("my_blog", "post_id")
print(post.title, post.created_at)
```

## Creating Posts

Use `PostBuilder` for a fluent API:

### Free Post

```python
from boostylib.builders import PostBuilder

post = (
    PostBuilder()
    .title("Hello World")
    .text("This is a free post for everyone!")
    .free()
    .build()
)
await client.posts.create_post("my_blog", post)
```

### Post for a Subscription Level

```python
levels = await client.subscriptions.get_levels("my_blog")
premium = next(l for l in levels if l.name == "Premium")

post = (
    PostBuilder()
    .title("Premium Content")
    .text("Only for premium subscribers")
    .access_level(level_id=str(premium.id))
    .teaser("Subscribe to Premium to see this!")
    .build()
)
await client.posts.create_post("my_blog", post)
```

### Post Unlocked by Donation

```python
post = (
    PostBuilder()
    .title("Donor Exclusive")
    .text("Thank you for your support!")
    .minimum_donation(amount=500, currency="RUB")
    .build()
)
await client.posts.create_post("my_blog", post)
```

### Post with Multiple Content Types

```python
post = (
    PostBuilder()
    .title("Rich Content Post")
    .text("Introduction paragraph")
    .image(url="https://example.com/photo.jpg")
    .text("More text after the image")
    .link(url="https://github.com", title="GitHub")
    .file(media_id="uploaded_file_id", filename="archive.zip")
    .tags(["devlog", "update"])
    .build()
)
```

### Scheduled Post

```python
from datetime import datetime, timezone

post = (
    PostBuilder()
    .title("Coming Soon")
    .text("This will be published later")
    .free()
    .scheduled_at(datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc))
    .build()
)
```

## Updating a Post

```python
updated_post = (
    PostBuilder()
    .title("Updated Title")
    .text("Updated content")
    .free()
    .build()
)
await client.posts.update_post("my_blog", "post_id", updated_post)
```

## Deleting a Post

```python
await client.posts.delete_post("my_blog", "post_id")
```
