from __future__ import annotations

from typing import Any

from app.core.jwt import create_access_token, decode_access_token, get_current_claims


def create_token(payload: dict[str, Any], expires_minutes: int) -> str:
    return create_access_token(payload, expires_minutes)


def decode_token(token: str) -> dict[str, Any]:
    return decode_access_token(token)
