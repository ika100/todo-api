# Design — 900 Count the todos with GET /todos/count

## Decisions

- **Count in the database, not in Python.** `SELECT count(*) FROM todos` runs as one statement through `Database.run` like every other query. It uses the same 2.5 s deadline and the same error mapping as spec 001, and it never loads rows into the process (AC-900.1, AC-900.2).
- **A literal GET-only route `/count` on the existing `/todos` router.** No `GET /todos/{id}` exists, so the literal path cannot collide with a GET id route. `PATCH` and `DELETE` on `/todos/count` keep reaching the existing `/{todo_id}` handlers: Starlette prefers a route that matches both path and method over one that matches only the path. Those handlers already answer `404 todo_not_found` for `count` because it does not parse as a UUID (AC-900.2). No method other than GET is registered on `/count`.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | lists the endpoint and links spec 900 | changed |

## Contract

`GET /todos/count` (no query parameters, no request body; any query string is ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of rows in `todos`, an integer `>= 0`. Exactly one key. `{"count": 0}` when there are no todos (AC-900.1, AC-900.2).
- Database failure or the 2.5 s deadline → `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`, exactly as for `GET /todos` (spec 001 design).

Unchanged, confirmed by AC-900.2:

- `PATCH /todos/count` with a valid body (for example `{"done": true}`) → `404 {"error": {"code": "todo_not_found", "message": <MSG_TODO_NOT_FOUND>}}`, identical to any non-UUID id. A body that fails validation still answers `422` first, as in spec 002's rule order.
- `DELETE /todos/count` → `404` with the same `todo_not_found` body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`, `/metrics`: no change.

Repository signature:

```python
async def count_todos(conn: AsyncConnection) -> int  # SELECT count(*) FROM todos
```

## Data

No schema change. `count(*)` on `todos` is a sequential or index-only scan; fine at todo-list scale.

## Risks

- None beyond those of spec 001. The count is a snapshot; a concurrent create or delete may or may not be included, which is acceptable for this endpoint.
