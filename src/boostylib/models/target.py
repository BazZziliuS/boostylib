"""Target (goal) model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from boostylib.enums import TargetType


class Target(BaseModel):
    """A blog fundraising or subscriber goal."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")

    id: int
    description: str = ""
    target_sum: int = Field(default=0, alias="targetSum")
    current_sum: int = Field(default=0, alias="currentSum")
    target_type: TargetType = Field(default=TargetType.MONEY, alias="type")
    blog_url: str = Field(default="", alias="bloggerUrl")
