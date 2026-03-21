# Authentication

Boosty does not provide an official public OAuth flow. Tokens are obtained manually from the browser.

## Getting Your Tokens

1. Log in to [boosty.to](https://boosty.to) in your browser
2. Open DevTools (`F12`) → **Application** tab → **Local Storage** → `https://boosty.to`
3. Find these keys:

| Key | Value | Maps to |
|---|---|---|
| `auth` | JSON object | `access_token`, `refresh_token`, `expires_at` |
| `_clentId` | UUID string | `device_id` |

!!! note
    The key is `_clentId` (with a typo) — this is intentional from Boosty's side.

## Authentication Methods

### Static Access Token

Simplest option. No auto-refresh — when the token expires you'll get `BoostyAuthError`.

```python
from boostylib import BoostyClient

async with BoostyClient(access_token="your_access_token") as client:
    user = await client.users.get_current_user()
```

### Full Credentials (with auto-refresh)

Recommended for long-running applications. The library automatically refreshes the token before it expires.

```python
from boostylib import BoostyClient, AuthCredentials

creds = AuthCredentials(
    access_token="...",
    refresh_token="...",
    device_id="...",
    expires_at=1710966525,
)

async with BoostyClient(credentials=creds) as client:
    # Token refreshes automatically
    user = await client.users.get_current_user()
```

### File Token Storage

Persists tokens to `~/.boosty/auth.json`. Survives restarts.

```python
from boostylib import BoostyClient
from boostylib.auth import FileTokenStorage

async with BoostyClient(token_storage=FileTokenStorage()) as client:
    user = await client.users.get_current_user()
```

The file is created with `chmod 600` (owner-only) on Unix systems.

### Environment Variables

Read-only storage from environment variables:

```bash
export BOOSTY_ACCESS_TOKEN=...
export BOOSTY_REFRESH_TOKEN=...
export BOOSTY_DEVICE_ID=...
export BOOSTY_EXPIRES_AT=1710966525
```

```python
from boostylib import BoostyClient
from boostylib.auth import EnvTokenStorage

async with BoostyClient(token_storage=EnvTokenStorage()) as client:
    ...
```

### Custom Storage

Implement the `TokenStorage` protocol for your own backend (Redis, database, etc.):

```python
from boostylib.auth.storage import TokenStorage, TokenPair

class RedisTokenStorage:
    async def load(self) -> TokenPair | None:
        data = await redis.get("boosty_tokens")
        ...

    async def save(self, tokens: TokenPair) -> None:
        await redis.set("boosty_tokens", tokens.model_dump_json())

    async def clear(self) -> None:
        await redis.delete("boosty_tokens")
```
