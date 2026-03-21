"""Event models for the event system."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from boostylib.enums import EventType
from boostylib.models.subscription import SubscriptionLevel
from boostylib.models.user import User


class Event(BaseModel):
    """Base event."""

    type: EventType
    blog_username: str
    timestamp: datetime


class DonationEvent(Event):
    """Fired when a new donation is received."""

    user: User
    amount: int
    currency: str
    message: str | None = None
    post_id: str | None = None


class SubscriptionEvent(Event):
    """Fired on subscription changes."""

    user: User
    level: SubscriptionLevel
    welcome_post_id: str | None = None


class CommentEvent(Event):
    """Fired when a new comment is posted."""

    user: User
    post_id: str
    comment_id: str
    content: str
