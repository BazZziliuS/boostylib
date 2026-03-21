# Middleware

Add custom logic to the HTTP request/response pipeline without modifying the library.

## Creating Middleware

Subclass `BaseMiddleware` and override the methods you need:

```python
from boostylib.http.middleware import BaseMiddleware
import httpx

class TimingMiddleware(BaseMiddleware):
    async def on_request(self, request: httpx.Request) -> httpx.Request:
        import time
        request.extensions["start_time"] = time.monotonic()
        return request

    async def on_response(self, response: httpx.Response) -> httpx.Response:
        import time
        elapsed = time.monotonic() - response.request.extensions["start_time"]
        print(f"{response.request.method} {response.request.url} took {elapsed:.3f}s")
        return response
```

## Registering Middleware

Pass a list of middleware instances to the client:

```python
from boostylib import BoostyClient

client = BoostyClient(
    access_token="...",
    middleware=[
        TimingMiddleware(),
        LoggingMiddleware(),
    ],
)
```

Middleware executes in registration order for requests, and in reverse order for responses.

## Available Methods

| Method | When | Use Case |
|---|---|---|
| `on_request(request)` | Before sending | Add headers, log, modify URL |
| `on_response(response)` | After receiving | Log, collect metrics, transform |
| `on_error(request, error)` | On exception | Alert, log errors |

## Example: Custom Headers

```python
class CustomHeadersMiddleware(BaseMiddleware):
    def __init__(self, headers: dict[str, str]):
        self.headers = headers

    async def on_request(self, request: httpx.Request) -> httpx.Request:
        request.headers.update(self.headers)
        return request

client = BoostyClient(
    access_token="...",
    middleware=[CustomHeadersMiddleware({"X-Source": "my-bot"})],
)
```

## Example: Error Alerting

```python
class AlertMiddleware(BaseMiddleware):
    async def on_error(self, request: httpx.Request, error: Exception) -> None:
        await send_alert(f"API error: {request.method} {request.url}: {error}")
```
