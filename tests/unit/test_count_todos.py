"""Unit tests for repository.count_todos (no real Postgres)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from todo_api.todos import repository


def conn_returning(row: Any) -> MagicMock:
    cur = MagicMock(fetchone=AsyncMock(return_value=row))
    return MagicMock(execute=AsyncMock(return_value=cur))


@pytest.mark.parametrize(("row", "expected"), [((3,), 3), ((0,), 0), (("7",), 7)])
async def test_count_todos_returns_int(row: Any, expected: int) -> None:
    conn = conn_returning(row)
    result = await repository.count_todos(conn)
    assert result == expected
    assert isinstance(result, int)
    conn.execute.assert_awaited_once()
    assert "count(*)" in conn.execute.await_args.args[0].lower()


async def test_count_todos_no_row_returns_zero() -> None:
    result = await repository.count_todos(conn_returning(None))
    assert result == 0
    assert isinstance(result, int)
