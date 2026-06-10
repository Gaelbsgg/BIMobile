from __future__ import annotations

from typing import Any


def success_response(data: Any, message: str | None = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"success": True, "data": data}
    if message is not None:
        payload["message"] = message
    if meta is not None:
        payload["meta"] = meta
    return payload


def error_response(message: str, details: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"success": False, "message": message}
    if details is not None:
        payload["details"] = details
    return payload
