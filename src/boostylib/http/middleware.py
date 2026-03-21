"""Middleware protocol and types for HTTP request/response pipeline."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import httpx


@runtime_checkable
class Middleware(Protocol):
    """Protocol for HTTP middleware.

    Middleware can intercept and modify requests before they are sent
    and responses after they are received.
    """

    async def on_request(self, request: httpx.Request) -> httpx.Request:
        """Called before sending a request. May modify and return the request."""
        ...

    async def on_response(self, response: httpx.Response) -> httpx.Response:
        """Called after receiving a response. May modify and return the response."""
        ...

    async def on_error(self, request: httpx.Request, error: Exception) -> None:
        """Called when a request fails with an exception."""
        ...


class BaseMiddleware:
    """Base middleware with no-op defaults. Subclass and override what you need."""

    async def on_request(self, request: httpx.Request) -> httpx.Request:
        return request

    async def on_response(self, response: httpx.Response) -> httpx.Response:
        return response

    async def on_error(self, request: httpx.Request, error: Exception) -> None:
        pass


class MiddlewareChain:
    """Executes a chain of middleware in order (request) and reverse order (response)."""

    def __init__(self, middlewares: list[Any] | None = None) -> None:
        self._middlewares: list[Any] = middlewares or []

    def add(self, middleware: Any) -> None:
        self._middlewares.append(middleware)

    async def process_request(self, request: httpx.Request) -> httpx.Request:
        for mw in self._middlewares:
            if hasattr(mw, "on_request"):
                request = await mw.on_request(request)
        return request

    async def process_response(self, response: httpx.Response) -> httpx.Response:
        for mw in reversed(self._middlewares):
            if hasattr(mw, "on_response"):
                response = await mw.on_response(response)
        return response

    async def process_error(self, request: httpx.Request, error: Exception) -> None:
        for mw in reversed(self._middlewares):
            if hasattr(mw, "on_error"):
                await mw.on_error(request, error)
