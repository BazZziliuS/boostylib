"""Subscriber model with full data including email and payments."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from boostylib.models.subscription import SubscriptionLevel


class Subscriber(BaseModel):
    """A subscriber to a blog — includes email and payment history."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: int
    name: str = ""
    email: str = ""
    avatar_url: str | None = Field(default=None, alias="avatarUrl")
    has_avatar: bool = Field(default=False, alias="hasAvatar")
    is_official: bool = Field(default=False, alias="isOfficial")
    level: SubscriptionLevel | None = None
    price: int = 0
    payments: float = 0.0
    status: str = "active"
    subscribed: bool = False
    on_time: int | None = Field(default=None, alias="onTime")
    off_time: int | None = Field(default=None, alias="offTime")
    is_black_listed: bool = Field(default=False, alias="isBlackListed")
    is_fee_paid: bool = Field(default=False, alias="isFeePaid")
    can_write: bool = Field(default=False, alias="canWrite")

    @property
    def is_active(self) -> bool:
        return self.status == "active" and self.subscribed

    @property
    def is_paid(self) -> bool:
        return self.price > 0
