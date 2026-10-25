# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed by the database (`SELECT count(*) FROM todos`) through the existing `db.run` path, not by loading the list in Python: that is the point of the endpoint (Problem). It inherits the existing 2.5 s deadline and the `503 unavailable` mapping unchanged.
- The route is a static `GET /todos/count` on the existing `/todos` router. No `GET /todos/{id}` route exists, and Starlette prefers a full (path + method) match over a partial one, so `PATCH /todos/count` and `DELETE /todos/count` keep falling through to `patch_todo` / `delete_todo`, where `parse_id("count")` is `None` and they answer `404 todo_not_found` (AC-900.2). No change to those handlers.

No ADR: nothing here outlives the feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body read)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`; the only key is `count` (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable within the deadline, exactly as `GET /todos`.
- Any query string is ignored (no filtering, non-goal).

Unchanged and binding for the tests (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → the same `404` body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready` behave as before.

## Data

No schema change. Query: `SELECT count(*) FROM todos`, returned as a Python `int`.

## Risks

- `count(*)` is a sequential scan on large tables; acceptable at this service's scale, and no filtering is planned.
