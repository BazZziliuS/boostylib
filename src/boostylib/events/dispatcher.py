"""Event dispatcher: routes events to registered handlers."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

from boostylib.enums import EventType
from boostylib.events.models import Event

logger = logging.getLogger("boostylib.events")

EventHandler = Callable[[Any], Coroutine[Any, Any, None]]


class EventDispatcher:
    """Routes events to registered async handlers."""

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)

    def on(self, event_type: EventType) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register an event handler.

        Example::

            @dispatcher.on(EventType.NEW_DONATION)
            async def handle_donation(event: DonationEvent):
                print(event.amount)
        """
        def decorator(func: EventHandler) -> EventHandler:
            self._handlers[event_type].append(func)
            return func
        return decorator

    def register(self, event_type: EventType, handler: EventHandler) -> None:
        """Programmatically register a handler."""
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: Event) -> None:
        """Dispatch an event to all registered handlers."""
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.exception(
                    "Error in handler %s for event %s",
                    handler.__name__,
                    event.type,
                )
