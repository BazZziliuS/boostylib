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
        """Called before sending a request.

        Args:
            request: Outgoing HTTP request.

        Returns:
            Modified or original HTTP request.
        """
        ...

    async def on_response(self, response: httpx.Response) -> httpx.Response:
        """Called after receiving a response.

        Args:
            response: Incoming HTTP response.

        Returns:
            Modified or original HTTP response.
        """
        ...

    async def on_error(self, request: httpx.Request, error: Exception) -> None:
        """Called when a request fails with an exception.

        Args:
            request: Failed HTTP request.
            error: Raised exception.
        """
        ...


class BaseMiddleware:
    """Base middleware with no-op defaults. Subclass and override what you need."""

    async def on_request(self, request: httpx.Request) -> httpx.Request:
        """Handle request.

        Args:
            request: Outgoing HTTP request.

        Returns:
            HTTP request.
        """
        return request

    async def on_response(self, response: httpx.Response) -> httpx.Response:
        """Handle response.

        Args:
            response: Incoming HTTP response.

        Returns:
            HTTP response.
        """
        return response

    async def on_error(self, request: httpx.Request, error: Exception) -> None:
        """Handle request error.

        Args:
            request: Failed HTTP request.
            error: Raised exception.
        """
        pass


class MiddlewareChain:
    """Executes a chain of middleware in order (request) and reverse order (response)."""

    def __init__(self, middlewares: list[Any] | None = None) -> None:
        """Initialize middleware chain.

        Args:
            middlewares: Optional initial list of middleware.
        """
        self._middlewares: list[Any] = middlewares or []

    def add(self, middleware: Any) -> None:
        """Add middleware to chain.

        Args:
            middleware: Middleware instance.
        """
        self._middlewares.append(middleware)

    async def process_request(self, request: httpx.Request) -> httpx.Request:
        """Process request through middleware in forward order.

        Args:
            request: Outgoing HTTP request.

        Returns:
            Processed HTTP request.
        """
        for mw in self._middlewares:
            if hasattr(mw, "on_request"):
                request = await mw.on_request(request)
        return request

    async def process_response(self, response: httpx.Response) -> httpx.Response:
        """Process response through middleware in reverse order.

        Args:
            response: Incoming HTTP response.

        Returns:
            Processed HTTP response.
        """
        for mw in reversed(self._middlewares):
            if hasattr(mw, "on_response"):
                response = await mw.on_response(response)
        return response

    async def process_error(self, request: httpx.Request, error: Exception) -> None:
        """Process error through middleware in reverse order.

        Args:
            request: Failed HTTP request.
            error: Raised exception.
        """
        for mw in reversed(self._middlewares):
            if hasattr(mw, "on_error"):
                await mw.on_error(request, error)
