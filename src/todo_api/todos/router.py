"""HTTP routes for /todos; serializes todos to the contract JSON."""

from __future__ import annotations

from datetime import UTC
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from todo_api.errors import MSG_TODO_NOT_FOUND, ApiError
from todo_api.todos import repository
from todo_api.todos.repository import Todo
from todo_api.todos.validation import parse_create, parse_id, parse_patch

router = APIRouter(prefix="/todos")


def to_json(todo: Todo) -> dict[str, Any]:
    created = todo.created_at.astimezone(UTC)
    stamp = created.strftime("%Y-%m-%dT%H:%M:%S") + f".{created.microsecond // 1000:03d}Z"
    return {
        "id": str(todo.id).lower(),
        "title": todo.title,
        "done": todo.done,
        "created_at": stamp,
    }


def _not_found() -> ApiError:
    return ApiError(404, "todo_not_found", MSG_TODO_NOT_FOUND)


@router.get("")
async def list_todos(request: Request) -> JSONResponse:
    todos = await request.app.state.db.run(repository.list_todos)
    return JSONResponse([to_json(t) for t in todos])


@router.post("")
async def create_todo(request: Request) -> JSONResponse:
    title = parse_create(await request.body())

    async def op(conn: Any) -> Todo:
        return await repository.create_todo(conn, title)

    todo = await request.app.state.db.run(op)
    return JSONResponse(to_json(todo), status_code=201)


@router.patch("/{todo_id}")
async def patch_todo(todo_id: str, request: Request) -> JSONResponse:
    req = parse_patch(await request.body())
    parsed = parse_id(todo_id)
    if parsed is None:
        raise _not_found()

    async def op(conn: Any) -> Todo | None:
        return await repository.update_todo(conn, parsed, title=req.title, done=req.done)

    todo = await request.app.state.db.run(op)
    if todo is None:
        raise _not_found()
    return JSONResponse(to_json(todo))


@router.delete("/{todo_id}")
async def delete_todo(todo_id: str, request: Request) -> Response:
    parsed = parse_id(todo_id)
    if parsed is None:
        raise _not_found()

    async def op(conn: Any) -> bool:
        return await repository.delete_todo(conn, parsed)

    if not await request.app.state.db.run(op):
        raise _not_found()
    return Response(status_code=204)
