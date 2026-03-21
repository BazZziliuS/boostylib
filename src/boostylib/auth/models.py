"""Auth data models."""

from __future__ import annotations

from pydantic import BaseModel, SecretStr


class TokenPair(BaseModel):
    """Token pair returned by Boosty auth."""

    access_token: SecretStr
    refresh_token: SecretStr
    device_id: str
    expires_at: int  # unix timestamp


class AuthCredentials(BaseModel):
    """Convenience wrapper for initial credentials."""

    access_token: SecretStr
    refresh_token: SecretStr
    device_id: str
    expires_at: int = 0
