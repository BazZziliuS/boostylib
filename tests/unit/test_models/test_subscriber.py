"""Tests for Subscriber model."""

from __future__ import annotations

import pytest

from boostylib.models.subscriber import Subscriber

pytestmark = pytest.mark.unit


class TestSubscriber:
    def test_from_api_data(self) -> None:
        raw = {
            "id": 12345,
            "name": "Test User",
            "email": "test@example.com",
            "avatarUrl": "https://img.example.com/avatar.jpg",
            "hasAvatar": True,
            "level": {"id": 1, "name": "Premium", "price": 500},
            "price": 500,
            "payments": 1500.0,
            "status": "active",
            "subscribed": True,
            "onTime": 1700000000,
            "isBlackListed": False,
            "canWrite": True,
        }
        sub = Subscriber.model_validate(raw)
        assert sub.id == 12345
        assert sub.email == "test@example.com"
        assert sub.payments == 1500.0
        assert sub.is_active is True
        assert sub.is_paid is True
        assert sub.level is not None
        assert sub.level.name == "Premium"

    def test_inactive_subscriber(self) -> None:
        sub = Subscriber(
            id=1,
            name="Gone",
            email="gone@mail.com",
            status="inactive",
            subscribed=False,
            price=0,
        )
        assert sub.is_active is False
        assert sub.is_paid is False

    def test_free_subscriber(self) -> None:
        sub = Subscriber(id=2, name="Free", email="free@mail.com", price=0, subscribed=True)
        assert sub.is_paid is False
