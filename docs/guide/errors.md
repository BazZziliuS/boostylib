# Error Handling

## Exception Hierarchy

All exceptions inherit from `BoostyError`:

```
BoostyError
├── BoostyAuthError          # 401 — invalid or expired token
├── BoostyForbiddenError     # 403 — insufficient permissions
├── BoostyNotFoundError      # 404 — resource not found
├── BoostyRateLimitError     # 429 — rate limit exceeded
├── BoostyServerError        # 5xx — server-side error
└── BoostyNetworkError       # Connection/timeout errors
```

## Catching Errors

```python
from boostylib.http.exceptions import (
    BoostyAuthError,
    BoostyError,
    BoostyNotFoundError,
    BoostyRateLimitError,
)

try:
    post = await client.posts.get_post("blog", "post_id")
except BoostyAuthError:
    # Token is invalid and refresh failed
    print("Re-authenticate required")
except BoostyNotFoundError:
    print("Post not found")
except BoostyRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except BoostyError as e:
    print(f"API error (status={e.status_code}): {e}")
```

## Automatic Retry

The library automatically retries on:

- **429 Too Many Requests** — respects `Retry-After` header
- **500, 502, 503, 504** — server errors

Retry behavior is configurable:

```python
from boostylib import BoostySettings

settings = BoostySettings(
    max_retries=5,          # default: 3
    retry_backoff_factor=1.0,  # default: 0.5
)
```

Retry delays use exponential backoff: `backoff_factor * 2^attempt`.

## Automatic Token Refresh

On a 401 response, the library:

1. Attempts to refresh the token using the stored `refresh_token`
2. Retries the original request with the new token
3. Raises `BoostyAuthError` only if refresh also fails

This is transparent — you don't need to handle it manually.

## BoostyRateLimitError

Has an extra `retry_after` field:

```python
except BoostyRateLimitError as e:
    if e.retry_after:
        await asyncio.sleep(e.retry_after)
```

## BoostyNetworkError

Wraps connection errors, DNS failures, and timeouts:

```python
except BoostyNetworkError as e:
    print(f"Network issue: {e}")
    print(f"Original error: {e.__cause__}")
```
