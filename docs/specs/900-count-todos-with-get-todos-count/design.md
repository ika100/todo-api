# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists to avoid transferring every row (AC-900.1).
- The route is a static `GET` path on the existing `/todos` router. No `GET /todos/{id}` route exists, so the static path cannot shadow one. `PATCH /todos/{todo_id}` and `DELETE /todos/{todo_id}` keep matching `count` as an id. `parse_id("count")` returns `None`, so both answer the existing `404 todo_not_found` without new code (AC-900.2).
- No ADR: the endpoint is local to this feature and follows the router/repository pattern already in place.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler, calls `count_todos` through `request.app.state.db.run` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`. The body has exactly one key, `count`, the number of rows in `todos` (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": ...}}` when the database is unreachable. This is the error every existing `/todos` endpoint already returns through `db.run` and the global handler.

Unchanged (AC-900.2):

- `PATCH /todos/count` with `{"done": true}` → `404 {"error": {"code": "todo_not_found", "message": <MSG_TODO_NOT_FOUND>}}`.
- `DELETE /todos/count` → the same `404 todo_not_found`.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their current behaviour.

## Data

No schema change. The query is `SELECT count(*) FROM todos` and reads the result as `int`.
