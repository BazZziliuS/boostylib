"""E2E test fixtures — require real Boosty credentials in env vars."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest

from boostylib import BoostyClient, BoostySettings
from boostylib.auth import EnvTokenStorage


def _has_credentials() -> bool:
    return bool(
        os.environ.get("BOOSTY_ACCESS_TOKEN")
        and os.environ.get("BOOSTY_DEVICE_ID")
    )


pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not _has_credentials(), reason="BOOSTY_ACCESS_TOKEN / BOOSTY_DEVICE_ID not set"),
]


@pytest.fixture
def blog_username() -> str:
    value = os.environ.get("BOOSTY_TEST_BLOG", "")
    if not value:
        pytest.skip("BOOSTY_TEST_BLOG not set")
    return value


@pytest.fixture
def settings() -> BoostySettings:
    return BoostySettings(
        timeout=15.0,
        max_retries=2,
        rate_limit_requests=30,
        rate_limit_period=60.0,
    )


@pytest.fixture
async def client(settings: BoostySettings) -> AsyncIterator[BoostyClient]:
    async with BoostyClient(
        token_storage=EnvTokenStorage(),
        settings=settings,
    ) as c:
        yield c
