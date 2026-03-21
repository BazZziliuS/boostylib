"""Donation model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from boostylib.models.user import User


class Donation(BaseModel):
    """A donation from a user."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: str
    user: User
    amount: int
    currency: str = "RUB"
    message: str | None = None
    created_at: datetime | int | None = Field(default=None, alias="createdAt")
