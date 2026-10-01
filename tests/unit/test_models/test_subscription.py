"""Tests for Subscription models."""

from __future__ import annotations

import pytest

from boostylib.models.subscription import SubscriptionLevel, SubscriptionStatus

pytestmark = pytest.mark.unit


class TestSubscriptionLevel:
    def test_free_level(self) -> None:
        level = SubscriptionLevel(id=0, name="Free", price=0, is_free=True)
        assert level.is_free is True
        assert level.currency == "RUB"

    def test_premium_level(self) -> None:
        level = SubscriptionLevel(id=1, name="Premium", price=500, is_free=False)
        assert level.price == 500


class TestSubscriptionStatus:
    def test_not_subscribed(self) -> None:
        status = SubscriptionStatus(is_subscribed=False)
        assert status.level is None
        assert status.is_paid is False

    def test_subscribed(self) -> None:
        level = SubscriptionLevel(id=1, name="Pro", price=1000)
        status = SubscriptionStatus(
            is_subscribed=True,
            level=level,
            is_paid=True,
            price=1000,
            currency="RUB",
        )
        assert status.is_subscribed is True
        assert status.level is not None
        assert status.level.name == "Pro"
