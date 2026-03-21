"""Tests for token storage implementations."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import SecretStr

from boostylib.auth.models import TokenPair
from boostylib.auth.storage import FileTokenStorage, MemoryTokenStorage

pytestmark = pytest.mark.unit


def _make_tokens() -> TokenPair:
    return TokenPair(
        access_token=SecretStr("access_123"),
        refresh_token=SecretStr("refresh_456"),
        device_id="device-uuid",
        expires_at=9999999999,
    )


class TestMemoryTokenStorage:
    async def test_save_and_load(self) -> None:
        storage = MemoryTokenStorage()
        tokens = _make_tokens()
        await storage.save(tokens)
        loaded = await storage.load()
        assert loaded is not None
        assert loaded.access_token.get_secret_value() == "access_123"
        assert loaded.device_id == "device-uuid"

    async def test_load_empty(self) -> None:
        storage = MemoryTokenStorage()
        assert await storage.load() is None

    async def test_clear(self) -> None:
        storage = MemoryTokenStorage()
        await storage.save(_make_tokens())
        await storage.clear()
        assert await storage.load() is None


class TestFileTokenStorage:
    async def test_save_and_load(self, tmp_path: Path) -> None:
        path = tmp_path / "auth.json"
        storage = FileTokenStorage(path=path)
        tokens = _make_tokens()
        await storage.save(tokens)

        assert path.exists()
        data = json.loads(path.read_text())
        assert data["access_token"] == "access_123"

        loaded = await storage.load()
        assert loaded is not None
        assert loaded.access_token.get_secret_value() == "access_123"

    async def test_load_nonexistent(self, tmp_path: Path) -> None:
        storage = FileTokenStorage(path=tmp_path / "missing.json")
        assert await storage.load() is None

    async def test_clear(self, tmp_path: Path) -> None:
        path = tmp_path / "auth.json"
        storage = FileTokenStorage(path=path)
        await storage.save(_make_tokens())
        await storage.clear()
        assert not path.exists()

    async def test_load_corrupted(self, tmp_path: Path) -> None:
        path = tmp_path / "auth.json"
        path.write_text("not json", encoding="utf-8")
        storage = FileTokenStorage(path=path)
        assert await storage.load() is None
