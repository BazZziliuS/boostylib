"""HTTP transport with auth injection, retry, rate limiting, and middleware."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import httpx

from boostylib.http.exceptions import (
    BoostyAuthError,
    BoostyForbiddenError,
    BoostyNetworkError,
    BoostyNotFoundError,
    BoostyRateLimitError,
    BoostyServerError,
)
from boostylib.http.middleware import MiddlewareChain
from boostylib.http.rate_limiter import RateLimiter
from boostylib.http.retry import RetryPolicy

if TYPE_CHECKING:
    from boostylib.auth.manager import AuthManager
    from boostylib.config import BoostySettings

logger = logging.getLogger("boostylib.http")

_SECRET_MASK_LEN = 8

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/146.0.0.0 Safari/537.36"
)


def _default_headers(auth_manager: AuthManager | None = None) -> dict[str, str]:
    """Browser-like default headers required by Boosty API for write operations."""
    headers: dict[str, str] = {
        "User-Agent": _USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://boosty.to",
        "Referer": "https://boosty.to/",
        "X-App": "web",
        "X-Locale": "ru_RU",
        "X-Referer": "boosty.to",
    }
    if auth_manager and auth_manager._tokens:
        headers["X-From-Id"] = auth_manager._tokens.device_id
    return headers


def _mask_token(token: str) -> str:
    if len(token) <= _SECRET_MASK_LEN:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


class HTTPTransport:
    """HTTP transport layer wrapping httpx.AsyncClient.

    Handles:
    - Bearer token injection
    - Automatic retry with exponential backoff
    - Rate limiting (token bucket)
    - Middleware pipeline
    - Logging with secret masking
    """

    def __init__(
        self,
        *,
        settings: BoostySettings,
        auth_manager: AuthManager | None = None,
        http_client: httpx.AsyncClient | None = None,
        middleware_chain: MiddlewareChain | None = None,
    ) -> None:
        self._settings = settings
        self._auth_manager = auth_manager
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            timeout=settings.timeout,
            headers=_default_headers(auth_manager),
        )
        self._retry = RetryPolicy(
            max_retries=settings.max_retries,
            backoff_factor=settings.retry_backoff_factor,
        )
        self._rate_limiter = RateLimiter(
            max_requests=settings.rate_limit_requests,
            period=settings.rate_limit_period,
        )
        self._middleware = middleware_chain or MiddlewareChain()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Send an HTTP request with retry, rate limiting, and auth.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API path relative to base_url (e.g. ``/blog/username/post/``).
            params: Query parameters.
            json: JSON body.
            data: Form data.
            files: Multipart file uploads.
            headers: Additional headers.

        Returns:
            httpx.Response on success.

        Raises:
            BoostyAuthError: On 401 after token refresh attempt.
            BoostyForbiddenError: On 403.
            BoostyNotFoundError: On 404.
            BoostyRateLimitError: On 429 after exhausting retries.
            BoostyServerError: On 5xx after exhausting retries.
            BoostyNetworkError: On connection/timeout errors.
        """
        url = f"{self._settings.base_url}{path}"
        merged_headers = dict(headers or {})

        for attempt in range(self._retry.max_retries + 1):
            await self._rate_limiter.acquire()

            # Inject auth token
            if self._auth_manager:
                token = await self._auth_manager.get_access_token()
                merged_headers["Authorization"] = f"Bearer {token}"

            request = self._client.build_request(
                method,
                url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=merged_headers,
            )

            # Middleware: on_request
            request = await self._middleware.process_request(request)

            self._log_request(request)

            try:
                response = await self._client.send(request)
            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
                await self._middleware.process_error(request, exc)
                if attempt < self._retry.max_retries:
                    await self._retry.wait(attempt, 0)
                    continue
                raise BoostyNetworkError(str(exc), cause=exc) from exc

            self._log_response(response)

            # Middleware: on_response
            response = await self._middleware.process_response(response)

            # Handle 401 → refresh token → retry once
            if response.status_code == 401 and self._auth_manager and attempt == 0:
                logger.info("Got 401, attempting token refresh")
                refreshed = await self._auth_manager.refresh()
                if refreshed:
                    continue
                raise BoostyAuthError()

            # Retryable statuses
            if self._retry.should_retry(response.status_code, attempt):
                retry_after = _parse_retry_after(response)
                await self._retry.wait(attempt, response.status_code, retry_after)
                continue

            # Non-retryable errors
            if response.status_code == 401:
                raise BoostyAuthError()
            if response.status_code == 403:
                raise BoostyForbiddenError(response.text)
            if response.status_code == 404:
                raise BoostyNotFoundError(response.text)
            if response.status_code == 429:
                retry_after = _parse_retry_after(response)
                raise BoostyRateLimitError(retry_after=retry_after)
            if response.status_code >= 500:
                raise BoostyServerError(response.text, status_code=response.status_code)

            return response

        # Should not reach here, but just in case
        raise BoostyServerError("Max retries exhausted")  # pragma: no cover

    def _log_request(self, request: httpx.Request) -> None:
        auth = request.headers.get("Authorization", "")
        masked = ""
        if auth.startswith("Bearer "):
            masked = f"Bearer {_mask_token(auth[7:])}"
        level = logging.DEBUG if not self._settings.debug else logging.INFO
        logger.log(level, "%s %s %s", request.method, request.url, masked)

    def _log_response(self, response: httpx.Response) -> None:
        level = logging.DEBUG if not self._settings.debug else logging.INFO
        logger.log(level, "%d %s (%.0f bytes)", response.status_code, response.url, len(response.content))

    async def close(self) -> None:
        """Close the underlying HTTP client if we own it."""
        if self._owns_client:
            await self._client.aclose()


def _parse_retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
