"""Tests for EventDispatcher."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from boostylib.enums import EventType
from boostylib.events.dispatcher import EventDispatcher
from boostylib.events.models import DonationEvent
from boostylib.models.user import User

pytestmark = pytest.mark.unit


def _make_donation_event() -> DonationEvent:
    return DonationEvent(
        type=EventType.NEW_DONATION,
        blog_username="testblog",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        user=User(id=1, name="donor"),
        amount=500,
        currency="RUB",
    )


class TestEventDispatcher:
    async def test_register_and_dispatch(self) -> None:
        dispatcher = EventDispatcher()
        received: list[DonationEvent] = []

        @dispatcher.on(EventType.NEW_DONATION)
        async def handler(event: DonationEvent) -> None:
            received.append(event)

        await dispatcher.dispatch(_make_donation_event())
        assert len(received) == 1
        assert received[0].amount == 500

    async def test_multiple_handlers(self) -> None:
        dispatcher = EventDispatcher()
        calls: list[str] = []

        @dispatcher.on(EventType.NEW_DONATION)
        async def handler1(event: DonationEvent) -> None:
            calls.append("h1")

        @dispatcher.on(EventType.NEW_DONATION)
        async def handler2(event: DonationEvent) -> None:
            calls.append("h2")

        await dispatcher.dispatch(_make_donation_event())
        assert calls == ["h1", "h2"]

    async def test_no_handler_for_event(self) -> None:
        dispatcher = EventDispatcher()
        # Should not raise
        await dispatcher.dispatch(_make_donation_event())

    async def test_handler_error_does_not_break_others(self) -> None:
        dispatcher = EventDispatcher()
        calls: list[str] = []

        @dispatcher.on(EventType.NEW_DONATION)
        async def bad_handler(event: DonationEvent) -> None:
            raise RuntimeError("boom")

        @dispatcher.on(EventType.NEW_DONATION)
        async def good_handler(event: DonationEvent) -> None:
            calls.append("ok")

        await dispatcher.dispatch(_make_donation_event())
        assert calls == ["ok"]

    async def test_programmatic_register(self) -> None:
        dispatcher = EventDispatcher()
        received: list[int] = []

        async def handler(event: DonationEvent) -> None:
            received.append(event.amount)

        dispatcher.register(EventType.NEW_DONATION, handler)
        await dispatcher.dispatch(_make_donation_event())
        assert received == [500]
