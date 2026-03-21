# Configuration

All client settings are managed through `BoostySettings`, which supports environment variables, TOML files, and programmatic overrides.

## Settings Reference

| Setting | Env Variable | Default | Description |
|---|---|---|---|
| `base_url` | `BOOSTY_BASE_URL` | `https://api.boosty.to/v1` | API base URL |
| `timeout` | `BOOSTY_TIMEOUT` | `30.0` | Request timeout in seconds |
| `max_retries` | `BOOSTY_MAX_RETRIES` | `3` | Max retry attempts |
| `retry_backoff_factor` | `BOOSTY_RETRY_BACKOFF_FACTOR` | `0.5` | Backoff multiplier |
| `rate_limit_requests` | `BOOSTY_RATE_LIMIT_REQUESTS` | `60` | Max requests per period |
| `rate_limit_period` | `BOOSTY_RATE_LIMIT_PERIOD` | `60.0` | Rate limit window (seconds) |
| `poll_interval` | `BOOSTY_POLL_INTERVAL` | `30.0` | Event polling interval (seconds) |
| `token_refresh_margin` | `BOOSTY_TOKEN_REFRESH_MARGIN` | `300` | Seconds before expiry to refresh |
| `cache_enabled` | `BOOSTY_CACHE_ENABLED` | `true` | Enable response caching |
| `cache_ttl_blog` | `BOOSTY_CACHE_TTL_BLOG` | `300` | Blog info cache TTL |
| `cache_ttl_levels` | `BOOSTY_CACHE_TTL_LEVELS` | `600` | Subscription levels cache TTL |
| `cache_ttl_user` | `BOOSTY_CACHE_TTL_USER` | `120` | User profile cache TTL |
| `cache_ttl_default` | `BOOSTY_CACHE_TTL_DEFAULT` | `60` | Default cache TTL |
| `debug` | `BOOSTY_DEBUG` | `false` | Enable debug logging |

## Priority Order

Settings are resolved in this order (first wins):

1. **Constructor arguments** — `BoostySettings(timeout=10.0)`
2. **Environment variables** — `BOOSTY_TIMEOUT=10`
3. **TOML config file** — `boosty.toml` (if `tomli` is available)
4. **Defaults** — hardcoded in the class

## Examples

### Environment Variables

```bash
export BOOSTY_TIMEOUT=10
export BOOSTY_MAX_RETRIES=5
export BOOSTY_DEBUG=true
```

### TOML File (`boosty.toml`)

```toml
timeout = 10.0
max_retries = 5
poll_interval = 60.0
debug = true
```

### Programmatic

```python
from boostylib import BoostyClient, BoostySettings

settings = BoostySettings(
    timeout=10.0,
    max_retries=5,
    rate_limit_requests=30,
    debug=True,
)

async with BoostyClient(settings=settings, access_token="...") as client:
    ...
```
