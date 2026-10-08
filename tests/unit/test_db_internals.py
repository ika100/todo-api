"""Unit tests for db.py internals and repository/router edge cases (no real Postgres)."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import psycopg
import pytest
from psycopg_pool import PoolTimeout

from todo_api import db as db_mod
from todo_api.db import Database
from todo_api.errors import DatabaseUnavailable
from todo_api.todos import repository
from todo_api.todos.router import to_json

URL = "postgresql://u:p@127.0.0.1:1/x"


def make_db(conn: Any = None, connect_exc: BaseException | None = None) -> Database:
    database = Database(URL, "SELECT 1;")
    conn = conn or MagicMock(execute=AsyncMock(), commit=AsyncMock())

    @asynccontextmanager
    async def connection() -> Any:
        if connect_exc is not None:
            raise connect_exc
        yield conn

    pool = MagicMock()
    pool.connection = connection
    database._pool = pool
    return database


async def test_run_returns_result_and_commits() -> None:
    conn = MagicMock(execute=AsyncMock(), commit=AsyncMock())
    database = make_db(conn)

    async def op(_: Any) -> int:
        return 42

    assert await database.run(op) == 42
    conn.commit.assert_awaited_once()


async def test_run_deadline_raises_unavailable_and_tracks_task(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(db_mod, "OP_DEADLINE_S", 0.05)
    database = make_db()
    database._schema_ready = True
    release = asyncio.Event()

    async def slow(_: Any) -> None:
        await release.wait()

    with pytest.raises(DatabaseUnavailable):
        await database.run(slow)
    assert len(db_mod._background_tasks) == 1
    release.set()
    await asyncio.sleep(0.05)
    assert not db_mod._background_tasks


async def test_abandoned_task_failure_is_consumed_and_cleaned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(db_mod, "OP_DEADLINE_S", 0.05)
    database = make_db()
    database._schema_ready = True

    async def slow_fail(_: Any) -> None:
        await asyncio.sleep(0.15)
        raise ValueError("boom")

    with pytest.raises(DatabaseUnavailable):
        await database.run(slow_fail)
    await asyncio.sleep(0.25)  # task fails after abandonment; callback logs, no "never retrieved"
    assert not db_mod._background_tasks


async def test_abandoned_task_cancelled_is_cleaned(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(db_mod, "OP_DEADLINE_S", 0.05)
    database = make_db()
    database._schema_ready = True

    async def forever(_: Any) -> None:
        await asyncio.Event().wait()

    with pytest.raises(DatabaseUnavailable):
        await database.run(forever)
    (task,) = tuple(db_mod._background_tasks)
    task.cancel()
    await asyncio.sleep(0.01)
    assert not db_mod._background_tasks


@pytest.mark.parametrize(
    "exc",
    [
        TimeoutError(),
        PoolTimeout(),
        psycopg.OperationalError("down"),
        psycopg.InterfaceError("closed"),
    ],
)
async def test_connection_errors_map_to_unavailable(exc: BaseException) -> None:
    database = make_db(connect_exc=exc)
    database._schema_ready = True

    async def op(_: Any) -> None:
        return None

    with pytest.raises(DatabaseUnavailable):
        await database.run(op)


async def test_deadline_missed_at_boundary_maps_to_unavailable() -> None:
    conn = MagicMock(execute=AsyncMock(), commit=AsyncMock(), rollback=AsyncMock())
    database = make_db(conn)
    database._schema_ready = True

    async def op(_: Any) -> None:
        return None

    # Deadline already in the past when the op returns: rolled back, answered as 503.
    async def late(op_: Any, _deadline: float) -> None:
        return await Database._guarded(database, op_, 0.0)

    database._guarded = late  # type: ignore[method-assign]
    with pytest.raises(DatabaseUnavailable):
        await database.run(op)
    conn.rollback.assert_awaited_once()
    conn.commit.assert_not_awaited()


async def test_non_connection_errors_propagate() -> None:
    database = make_db()
    database._schema_ready = True

    async def op(_: Any) -> None:
        raise ValueError("bug")

    with pytest.raises(ValueError, match="bug"):
        await database.run(op)


async def test_ensure_schema_runs_once_under_concurrency() -> None:
    conn = MagicMock(execute=AsyncMock(), commit=AsyncMock())
    database = make_db(conn)
    await asyncio.gather(*(database.ensure_schema() for _ in range(5)))
    assert database._schema_ready
    # one advisory lock call + one schema call, not five
    assert conn.execute.await_count == 2
    assert "pg_advisory_xact_lock" in conn.execute.await_args_list[0].args[0]
    assert conn.execute.await_args_list[0].args[1] == (db_mod.SCHEMA_LOCK_ID,)


async def test_ensure_schema_failure_leaves_flag_unset_and_retries() -> None:
    database = make_db(connect_exc=psycopg.OperationalError("down"))
    with pytest.raises(psycopg.OperationalError):
        await database.ensure_schema()
    assert not database._schema_ready
    assert not database._schema_lock.locked()


async def test_run_ensures_schema_first() -> None:
    conn = MagicMock(execute=AsyncMock(), commit=AsyncMock())
    database = make_db(conn)

    async def op(_: Any) -> str:
        return "ok"

    assert await database.run(op) == "ok"
    assert database._schema_ready


async def test_open_swallows_failure_and_close_closes_pool() -> None:
    database = make_db(connect_exc=psycopg.OperationalError("down"))
    database._pool.open = AsyncMock()
    database._pool.close = AsyncMock()
    await database.open()  # must not raise
    database._pool.open.assert_awaited_once_with(wait=False)
    assert not database._schema_ready
    await database.close()
    database._pool.close.assert_awaited_once_with(timeout=5)


async def test_ping_executes_select_one() -> None:
    conn = MagicMock(execute=AsyncMock(), commit=AsyncMock())
    database = make_db(conn)
    database._schema_ready = True
    await database.ping()
    conn.execute.assert_awaited_once_with("SELECT 1")


async def test_create_todo_without_row_raises() -> None:
    cur = MagicMock(execute=AsyncMock(), fetchone=AsyncMock(return_value=None))
    cur.__aenter__ = AsyncMock(return_value=cur)
    cur.__aexit__ = AsyncMock(return_value=False)
    conn = MagicMock(cursor=MagicMock(return_value=cur))
    with pytest.raises(RuntimeError):
        await repository.create_todo(conn, "x")


async def test_delete_todo_rowcount() -> None:
    for count, expected in ((1, True), (0, False)):
        conn = MagicMock(execute=AsyncMock(return_value=MagicMock(rowcount=count)))
        assert await repository.delete_todo(conn, UUID(int=1)) is expected


def _todo(created: datetime) -> repository.Todo:
    return repository.Todo(UUID("ABCDEFAB-0000-4000-8000-000000000001"), "t", True, created)


def test_to_json_formats_utc_millis_and_lowercase_id() -> None:
    out = to_json(_todo(datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=UTC)))
    assert out == {
        "id": "abcdefab-0000-4000-8000-000000000001",
        "title": "t",
        "done": True,
        "created_at": "2026-01-02T03:04:05.678Z",
    }


def test_to_json_converts_offset_and_pads_millis() -> None:
    tz = timezone(timedelta(hours=2))
    out = to_json(_todo(datetime(2026, 1, 2, 5, 4, 5, 7000, tzinfo=tz)))
    assert out["created_at"] == "2026-01-02T03:04:05.007Z"
