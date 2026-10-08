"""Pure request parsing; applies the contract's rule order without touching the database."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from todo_api.errors import MSG_INVALID_REQUEST, MSG_TITLE_REQUIRED, MSG_TITLE_TOO_LONG, ApiError

MAX_TITLE_LENGTH = 200


@dataclass(frozen=True)
class PatchRequest:
    title: str | None  # stripped; None = not in the request
    done: bool | None  # None = not in the request


def _invalid() -> ApiError:
    return ApiError(422, "invalid_request", MSG_INVALID_REQUEST)


def _load_object(raw: bytes) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except (ValueError, RecursionError):
        raise _invalid() from None
    if not isinstance(data, dict):
        raise _invalid()
    return data


def _parse_title(value: object) -> str:
    if value is None:
        raise ApiError(422, "title_required", MSG_TITLE_REQUIRED)
    if not isinstance(value, str):
        raise _invalid()
    stripped = value.strip()
    if stripped == "":
        raise ApiError(422, "title_required", MSG_TITLE_REQUIRED)
    if len(stripped) > MAX_TITLE_LENGTH:
        raise ApiError(422, "title_too_long", MSG_TITLE_TOO_LONG)
    return stripped


def parse_create(raw: bytes) -> str:
    """Return the stripped title of a POST /todos body or raise ApiError."""
    return _parse_title(_load_object(raw).get("title"))


def parse_patch(raw: bytes) -> PatchRequest:
    """Return the fields of a PATCH /todos/{id} body or raise ApiError."""
    data = _load_object(raw)
    if "title" not in data and "done" not in data:
        raise _invalid()
    done: bool | None = None
    if "done" in data:
        if not isinstance(data["done"], bool):
            raise _invalid()
        done = data["done"]
    title = _parse_title(data["title"]) if "title" in data else None
    return PatchRequest(title=title, done=done)


def parse_id(value: str) -> UUID | None:
    """Return the UUID, or None when the value is not a UUID."""
    try:
        return UUID(value)
    except (ValueError, AttributeError, TypeError):
        return None
