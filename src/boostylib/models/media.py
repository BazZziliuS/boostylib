"""Media file model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MediaFile(BaseModel):
    """An uploaded media file."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    id: str
    url: str
    signed_url: str | None = None
    filename: str | None = None
    size: int | None = None
    content_type: str | None = None
    width: int | None = None
    height: int | None = None
    duration: float | None = None
