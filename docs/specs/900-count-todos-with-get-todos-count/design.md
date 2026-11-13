# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: avoiding the full read is the point of the feature (Problem).
- `GET /todos/count` is a static route on the existing `/todos` router. There is no `GET /todos/{todo_id}`, so nothing it could shadow. `PATCH /todos/{todo_id}` and `DELETE /todos/{todo_id}` stay as they are: `parse_id("count")` returns `None`, so they already answer `404 todo_not_found` for `count` (AC-900.2). No method-specific route is added for `count`, so `PATCH`/`DELETE` keep reaching the id handlers.
- No ADR: this is a feature-local choice.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` (`SELECT count(*) FROM todos`) | changed |
| `src/todo_api/todos/router.py` | `@router.get("/count") async def count_todos(request) -> JSONResponse` via `request.app.state.db.run(repository.count_todos)` | changed |

## Contract

`GET /todos/count`, no query parameters, no body.

- `200`, `Content-Type: application/json`, body `{"count": <int>}`. `count` is a non-negative JSON integer equal to the number of rows in `todos`, e.g. `{"count": 3}` (AC-900.1) or `{"count": 0}` (AC-900.2). The body has no other fields.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable (the existing `DatabaseUnavailable` handler, same as `GET /todos`).

Unchanged id routes, called with the literal `count` (AC-900.2):

- `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. Body validation still runs first, as for any id (an invalid body answers `422` as before).
- `DELETE /todos/count` → `404` with the same `todo_not_found` body.

All other endpoints (`GET /todos`, `POST /todos`, `PATCH`/`DELETE /todos/{id}`, `/health`, `/ready`) do not change.

## Data

No schema change; read-only query on the existing `todos` table.
