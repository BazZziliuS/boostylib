"""Media upload API."""

from __future__ import annotations

from pathlib import Path
from typing import IO, Any

from boostylib.api.base import BaseAPI
from boostylib.models.media import MediaFile


class MediaAPI(BaseAPI):
    """Endpoints for media file uploads."""

    async def upload_image(
        self,
        file: Path | IO[bytes],
        *,
        content_type: str = "image/png",
    ) -> MediaFile:
        """Upload an image file."""
        return await self._upload(file, content_type=content_type)

    async def upload_file(
        self,
        file: Path | IO[bytes],
        *,
        filename: str | None = None,
    ) -> MediaFile:
        """Upload a generic file (archive, document, etc.)."""
        return await self._upload(file, filename=filename)

    async def upload_video(self, file: Path | IO[bytes]) -> MediaFile:
        """Upload a video file."""
        return await self._upload(file, content_type="video/mp4")

    async def upload_audio(self, file: Path | IO[bytes]) -> MediaFile:
        """Upload an audio file."""
        return await self._upload(file, content_type="audio/mpeg")

    async def _upload(
        self,
        file: Path | IO[bytes],
        *,
        content_type: str | None = None,
        filename: str | None = None,
    ) -> MediaFile:
        """Internal upload handler."""
        if isinstance(file, Path):
            filename = filename or file.name
            file_bytes = file.read_bytes()
        else:
            file_bytes = file.read()
            filename = filename or getattr(file, "name", "upload")

        files_payload: dict[str, Any] = {"file": (filename, file_bytes)}
        if content_type:
            files_payload["file"] = (filename, file_bytes, content_type)

        response = await self._transport.request(
            "POST",
            "/upload/",
            files=files_payload,
        )
        data = response.json()
        return MediaFile.model_validate(data)
