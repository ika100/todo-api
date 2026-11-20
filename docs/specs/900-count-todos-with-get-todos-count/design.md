# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists so nobody downloads the list (Problem), and the server should not either.
- The route is a static `GET /count` on the existing `/todos` router; no `GET /{todo_id}` route exists, and Starlette prefers a full path+method match over a path-only match, so `PATCH`/`DELETE /todos/count` keep reaching the id routes, where `parse_id("count")` is `None` and they answer `404 todo_not_found` exactly as today (AC-900.2). No change to the id routes is needed.
- No ADR: a feature-local endpoint following the existing router/repository pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler, runs `count_todos` through `request.app.state.db.run` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}` — the number of rows in `todos` (AC-900.1, AC-900.2). Exactly one key, `count`, a JSON integer.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable, via the existing `DatabaseUnavailable` handler (same as `GET /todos`).
- Other methods on `/todos/count`: `PATCH` (body validated first, as today) and `DELETE` answer `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). `POST /todos/count` stays `405 method_not_allowed` as today.

All existing endpoints are unchanged.

## Data

No schema change; `count(*)` on the existing `todos` table.
