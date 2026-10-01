"""E2E test fixtures — require real Boosty credentials in env vars."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from boostylib import BoostyClient, BoostySettings
from boostylib.auth import EnvTokenStorage

# Automatically load .env file if present
_env_file = Path(".env")
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), val)


def _has_credentials() -> bool:
    return bool(os.environ.get("BOOSTY_ACCESS_TOKEN") and os.environ.get("BOOSTY_DEVICE_ID"))


pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not _has_credentials(), reason="BOOSTY_ACCESS_TOKEN / BOOSTY_DEVICE_ID not set"
    ),
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
