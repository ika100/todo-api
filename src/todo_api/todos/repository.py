"""Todo table definition and parameterized queries on an async psycopg connection."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import class_row

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS todos (
    id         uuid        PRIMARY KEY,
    title      text        NOT NULL CHECK (char_length(title) BETWEEN 1 AND 200),
    done       boolean     NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT date_trunc('milliseconds', clock_timestamp())
);
CREATE INDEX IF NOT EXISTS todos_created_at_id_idx ON todos (created_at, id);
"""


@dataclass(frozen=True)
class Todo:
    id: UUID
    title: str
    done: bool
    created_at: datetime


async def list_todos(conn: AsyncConnection) -> list[Todo]:
    async with conn.cursor(row_factory=class_row(Todo)) as cur:
        await cur.execute("SELECT id, title, done, created_at FROM todos ORDER BY created_at, id")
        return await cur.fetchall()


async def create_todo(conn: AsyncConnection, title: str) -> Todo:
    async with conn.cursor(row_factory=class_row(Todo)) as cur:
        await cur.execute(
            "INSERT INTO todos (id, title) VALUES (%s, %s) RETURNING id, title, done, created_at",
            (uuid.uuid4(), title),
        )
        row = await cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING returned no row")
    return row


async def set_done(conn: AsyncConnection, todo_id: UUID, done: bool) -> Todo | None:
    async with conn.cursor(row_factory=class_row(Todo)) as cur:
        await cur.execute(
            "UPDATE todos SET done = %s WHERE id = %s RETURNING id, title, done, created_at",
            (done, todo_id),
        )
        return await cur.fetchone()


async def delete_todo(conn: AsyncConnection, todo_id: UUID) -> bool:
    cur = await conn.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    return cur.rowcount == 1
