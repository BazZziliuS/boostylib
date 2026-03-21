"""Tests for SyncBoostyClient."""

from __future__ import annotations

import pytest
import respx
import httpx

from boostylib.sync import SyncBoostyClient
from boostylib import BoostySettings

pytestmark = pytest.mark.unit


class TestSyncClient:
    @respx.mock
    def test_sync_get_user(self) -> None:
        """Test synchronous API call through SyncBoostyClient."""
        respx.get("https://api.boosty.to/v1/user/current").mock(
            return_value=httpx.Response(200, json={
                "id": 123,
                "name": "TestUser",
                "hasAvatar": False,
            })
        )

        settings = BoostySettings(
            timeout=5.0,
            max_retries=0,
            rate_limit_requests=1000,
            cache_enabled=False,
        )

        with SyncBoostyClient(access_token="test_token", settings=settings) as client:
            user = client.users.get_current_user()
            assert user.id == 123
            assert user.name == "TestUser"
