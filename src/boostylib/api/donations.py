"""Donations API."""

from __future__ import annotations

from typing import Any, AsyncIterator

from boostylib.api.base import BaseAPI
from boostylib.models.donation import Donation
from boostylib.models.pagination import PaginatedResponse


class DonationsAPI(BaseAPI):
    """Endpoints for donation tracking."""

    async def get_donations(
        self,
        username: str,
        *,
        limit: int = 20,
        offset: str | None = None,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> PaginatedResponse[Donation]:
        """Get donations with filtering and pagination."""
        params: dict[str, Any] = {"limit": limit}
        if offset is not None:
            params["offset"] = offset
        if from_ts is not None:
            params["from_ts"] = from_ts
        if to_ts is not None:
            params["to_ts"] = to_ts

        data = await self._get(f"/blog/{username}/donations/", params=params)
        return self._parse_paginated(data, Donation)

    async def iter_donations(
        self,
        username: str,
        *,
        limit: int = 20,
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> AsyncIterator[Donation]:
        """Async iterate over all donations."""
        params: dict[str, Any] = {}
        if from_ts is not None:
            params["from_ts"] = from_ts
        if to_ts is not None:
            params["to_ts"] = to_ts
        async for donation in self._iter_pages(
            f"/blog/{username}/donations/", Donation, params=params, limit=limit
        ):
            yield donation
