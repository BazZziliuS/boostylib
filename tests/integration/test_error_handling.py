"""Integration tests for error handling."""

from __future__ import annotations

import httpx
import pytest
import respx

from boostylib import BoostyClient
from boostylib.http.exceptions import (
    BoostyAuthError,
    BoostyForbiddenError,
    BoostyNotFoundError,
    BoostyRateLimitError,
)

pytestmark = pytest.mark.integration


class TestErrorHandling:
    @respx.mock
    async def test_401_raises_auth_error(self, client: BoostyClient) -> None:
        # Mock both the request and the token refresh to fail
        respx.get("https://api.boosty.to/v1/blog/test/post/").mock(
            return_value=httpx.Response(401, json={"error": "unauthorized"})
        )
        respx.post("https://api.boosty.to/oauth/token/").mock(
            return_value=httpx.Response(401, json={"error": "invalid_token"})
        )
        with pytest.raises(BoostyAuthError):
            await client.posts.list_posts("test")

    @respx.mock
    async def test_403_raises_forbidden(self, client: BoostyClient) -> None:
        respx.get("https://api.boosty.to/v1/blog/test/post/").mock(
            return_value=httpx.Response(403, text="Forbidden")
        )
        with pytest.raises(BoostyForbiddenError):
            await client.posts.list_posts("test")

    @respx.mock
    async def test_404_raises_not_found(self, client: BoostyClient) -> None:
        respx.get("https://api.boosty.to/v1/blog/test/post/missing").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        with pytest.raises(BoostyNotFoundError):
            await client.posts.get_post("test", "missing")

    @respx.mock
    async def test_429_raises_rate_limit(self, client: BoostyClient) -> None:
        respx.get("https://api.boosty.to/v1/blog/test/post/").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "30"})
        )
        with pytest.raises(BoostyRateLimitError) as exc_info:
            await client.posts.list_posts("test")
        assert exc_info.value.retry_after == 30.0
