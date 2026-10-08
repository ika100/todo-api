"""Postgres access: connection pool, operation deadline, error mapping, schema."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import psycopg
import structlog
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool, PoolTimeout

from todo_api.errors import DatabaseUnavailable

OP_DEADLINE_S = 2.5
SCHEMA_LOCK_ID = 7_431_001_001

T = TypeVar("T")

logger = structlog.get_logger()

# Tasks abandoned after a deadline; kept so they are not garbage collected mid-flight.
_background_tasks: set[asyncio.Task[object]] = set()

_CONNECTION_ERRORS = (
    TimeoutError,
    PoolTimeout,
    psycopg.OperationalError,
    psycopg.InterfaceError,
)


def _consume(task: asyncio.Task[object]) -> None:
    _background_tasks.discard(task)
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.warning("database_abandoned_operation_failed", error=type(exc).__name__)


class Database:
    """Owns the pool; every operation answers within OP_DEADLINE_S."""

    def __init__(self, url: str, schema_sql: str) -> None:
        self._schema_sql = schema_sql
        self._schema_ready = False
        self._schema_lock = asyncio.Lock()
        self._pool = AsyncConnectionPool(
            url,
            min_size=1,
            max_size=5,
            open=False,
            timeout=2.0,
            kwargs={"connect_timeout": 2},
            check=AsyncConnectionPool.check_connection,
        )

    async def open(self) -> None:
        await self._pool.open(wait=False)
        try:
            await asyncio.wait_for(self.ensure_schema(), timeout=OP_DEADLINE_S)
        except Exception as exc:
            logger.warning("database_unavailable", error=type(exc).__name__)

    async def close(self) -> None:
        await self._pool.close(timeout=5)

    async def ensure_schema(self) -> None:
        async with self._schema_lock:
            if self._schema_ready:
                return
            async with self._pool.connection() as conn:
                await conn.execute("SELECT pg_advisory_xact_lock(%s)", (SCHEMA_LOCK_ID,))
                await conn.execute(self._schema_sql.encode())
            self._schema_ready = True

    async def _guarded(self, op: Callable[[AsyncConnection], Awaitable[T]]) -> T:
        if not self._schema_ready:
            await self.ensure_schema()
        async with self._pool.connection() as conn:
            result = await op(conn)
            await conn.commit()
            return result

    async def run(self, op: Callable[[AsyncConnection], Awaitable[T]]) -> T:
        task: asyncio.Task[T] = asyncio.ensure_future(self._guarded(op))
        done, _ = await asyncio.wait({task}, timeout=OP_DEADLINE_S)
        if not done:
            _background_tasks.add(task)
            task.add_done_callback(_consume)
            logger.warning("database_unavailable", error="DeadlineExceeded")
            raise DatabaseUnavailable
        try:
            return task.result()
        except _CONNECTION_ERRORS as exc:
            logger.warning("database_unavailable", error=type(exc).__name__)
            raise DatabaseUnavailable from exc

    async def ping(self) -> None:
        async def _select_one(conn: AsyncConnection) -> None:
            await conn.execute("SELECT 1")

        await self.run(_select_one)
