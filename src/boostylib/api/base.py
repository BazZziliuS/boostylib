"""Base class for API endpoint groups."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

from boostylib.models.pagination import PaginatedResponse

if TYPE_CHECKING:
    from boostylib.http.transport import HTTPTransport

T = TypeVar("T", bound=BaseModel)


class BaseAPI:
    """Base API class providing HTTP transport access."""

    def __init__(self, transport: HTTPTransport) -> None:
        self._transport = transport

    async def _get(self, path: str, **kwargs: Any) -> Any:
        response = await self._transport.request("GET", path, **kwargs)
        return response.json()

    async def _post(self, path: str, **kwargs: Any) -> Any:
        response = await self._transport.request("POST", path, **kwargs)
        return response.json()

    async def _put(self, path: str, **kwargs: Any) -> Any:
        response = await self._transport.request("PUT", path, **kwargs)
        return response.json()

    async def _delete(self, path: str, **kwargs: Any) -> None:
        await self._transport.request("DELETE", path, **kwargs)

    async def _iter_pages(
        self,
        path: str,
        model_cls: type[T],
        *,
        params: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> AsyncIterator[T]:
        """Async iterate over all pages of a paginated endpoint."""
        offset: str | None = None
        while True:
            request_params = dict(params or {})
            request_params["limit"] = limit
            if offset is not None:
                request_params["offset"] = offset

            data = await self._get(path, params=request_params)
            page = self._parse_paginated(data, model_cls)
            for item in page.data:
                yield item

            if page.is_last or page.cursor is None:
                break
            offset = page.cursor

    def _parse_paginated(self, data: dict[str, Any], model_cls: type[T]) -> PaginatedResponse[T]:
        """Parse a raw paginated API response."""
        items_raw = data.get("data", [])
        extra = data.get("extra", {})
        items = [model_cls.model_validate(item) for item in items_raw]
        return PaginatedResponse(
            data=items,
            cursor=extra.get("offset"),
            is_last=extra.get("isLast", True),
        )
