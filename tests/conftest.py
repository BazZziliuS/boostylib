"""Shared test fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from pydantic import SecretStr

from boostylib import BoostyClient, BoostySettings
from boostylib.auth.models import TokenPair
from boostylib.auth.storage import MemoryTokenStorage


@pytest.fixture
def settings() -> BoostySettings:
    return BoostySettings(
        base_url="https://api.boosty.to/v1",
        timeout=5.0,
        max_retries=1,
        rate_limit_requests=1000,
        rate_limit_period=1.0,
        cache_enabled=False,
    )


@pytest.fixture
def token_pair() -> TokenPair:
    return TokenPair(
        access_token=SecretStr("test_access_token_64chars_" + "a" * 38),
        refresh_token=SecretStr("test_refresh_token_64chars_" + "b" * 37),
        device_id="test-device-id-uuid",
        expires_at=9999999999,
    )


@pytest.fixture
def memory_storage(token_pair: TokenPair) -> MemoryTokenStorage:
    storage = MemoryTokenStorage()
    storage._tokens = token_pair
    return storage


@pytest.fixture
async def client(settings: BoostySettings, memory_storage: MemoryTokenStorage) -> AsyncIterator[BoostyClient]:
    async with BoostyClient(
        token_storage=memory_storage,
        settings=settings,
    ) as c:
        yield c
