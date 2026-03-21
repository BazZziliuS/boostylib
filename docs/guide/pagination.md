# Pagination

All list endpoints return `PaginatedResponse[T]` and support both manual and automatic pagination.

## Manual Pagination

```python
page = await client.posts.list_posts("my_blog", limit=10)

for post in page.data:
    print(post.title)

print(f"Last page: {page.is_last}")
print(f"Cursor: {page.cursor}")
```

### Fetching the Next Page

```python
page = await client.posts.list_posts("my_blog", limit=10)
while not page.is_last:
    for post in page.data:
        process(post)
    page = await client.posts.list_posts("my_blog", limit=10, offset=page.cursor)
```

## Async Iterator

The simplest way — auto-paginate through all items:

```python
async for post in client.posts.iter_posts("my_blog"):
    print(post.title)
```

Available on:

- `client.posts.iter_posts()`
- `client.donations.iter_donations()`
- `client.comments.iter_comments()`
- `client.subscriptions.iter_subscribers()`

## PaginatedResponse Fields

| Field | Type | Description |
|---|---|---|
| `data` | `list[T]` | Items on this page |
| `cursor` | `str \| None` | Opaque cursor for the next page |
| `is_last` | `bool` | Whether this is the final page |
| `total` | `int \| None` | Total count (if provided by API) |
