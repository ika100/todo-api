# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count comes from one `SELECT count(*) FROM todos` through the existing `db.run` path (same deadline, same `503 unavailable` mapping as every other endpoint), not from loading the list: the point of the endpoint is to not transfer the rows (Problem).
- `GET /todos/count` is a static route on the existing `/todos` router. No `GET /todos/{id}` route exists, and Starlette prefers a full (path + method) match over a path-only match, so `PATCH /todos/count` and `DELETE /todos/count` still reach the `/{todo_id}` handlers. `parse_id("count")` returns `None` there, so they answer `404 todo_not_found` like any non-UUID id (AC-900.2). No handler for `PATCH`/`DELETE` on `/count` is added.
- No ADR: every choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query string is ignored)
→ `200`, `Content-Type: application/json`, body `{"count": <int ≥ 0>}` (AC-900.1, AC-900.2). The body has exactly one key, `count`, a JSON integer.

Errors use the existing error body `{"error": {"code": str, "message": str}}`:

- Database unreachable within the existing deadline → `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`, exactly as for `GET /todos`.
- `PATCH /todos/count` (any body that passes `parse_patch`, e.g. `{"done": true}`) and `DELETE /todos/count` → `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). A PATCH body that fails validation keeps answering `422` first, as for any id (unchanged rule order of spec 002).
- `POST /todos/count` and `PUT /todos/count` → `405 method_not_allowed` (existing generic handler; not a criterion).

All other endpoints are unchanged (AC-900.2).

## Data

No schema change. Query: `SELECT count(*) FROM todos` → one row, one `bigint`, returned as `int`.
