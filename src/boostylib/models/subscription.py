"""Subscription models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionLevel(BaseModel):
    """A subscription tier for a blog."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: int
    name: str = ""
    price: int = 0
    currency: str = "RUB"
    is_free: bool = False
    owner_id: int | None = Field(default=None, alias="ownerId")
    is_archived: bool = Field(default=False, alias="isArchived")
    currency_prices: dict[str, float] = Field(default_factory=dict, alias="currencyPrices")


class UserSubscription(BaseModel):
    """A user's subscription to a blog."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    blog_url: str
    level: SubscriptionLevel
    is_paid: bool = False
    expires_at: datetime | None = None


class SubscriptionStatus(BaseModel):
    """Result of subscription verification."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    is_subscribed: bool
    level: SubscriptionLevel | None = None
    expires_at: datetime | None = None
    is_paid: bool = False
    price: int | None = None
    currency: str | None = None
