# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list and taking its length, because the point of this feature is to avoid moving every row (Problem).
- Only a `GET` route is added at `/todos/count`. The `PATCH /todos/{todo_id}` and `DELETE /todos/{todo_id}` routes stay as they are. Starlette routes by path and method, so `PATCH`/`DELETE /todos/count` still reach the id routes. There, `parse_id("count")` returns `None` and the routes answer the existing `404 todo_not_found` (AC-900.2). No special case for the literal `count` is added.
- The count goes through `request.app.state.db.run(...)` like every other query, so it gets the same deadline and the same `503 unavailable` behaviour when the database is unreachable as `GET /todos`.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` | changed |
| `src/todo_api/todos/router.py` | `@router.get("/count")` handler `count_todos(request) -> JSONResponse` | changed |

## Contract

`GET /todos/count` takes no query parameters and no body.

- `200`, `Content-Type: application/json`, body `{"count": <int>}`. `count` is a non-negative integer equal to the number of rows in `todos` (AC-900.1: `{"count": 3}` with three todos; AC-900.2: `{"count": 0}` with none). The body has no other fields.
- `503` with `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable. This is the same behaviour as every other `/todos` endpoint and comes from the existing error handler.

Unchanged (AC-900.2):
- `PATCH /todos/count` with a valid body such as `{"done": true}` returns `404` with `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` returns the same `404` body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their current contracts.

## Data

No schema change: the query reads the existing `todos` table.
