# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the point of the endpoint is to avoid transferring every row (Problem).
- The route is a static path `GET /todos/count` on the existing `/todos` router. There is no `GET /todos/{todo_id}` route, so nothing is shadowed for GET; `PATCH`/`DELETE /todos/count` still match the existing `/{todo_id}` routes, where `parse_id("count")` returns `None` and the handler answers `404 todo_not_found` exactly as for any unknown id (AC-900.2). No change to those handlers.
- No ADR: a feature-local endpoint, no new pattern or dependency.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler, runs `count_todos` through `request.app.state.db.run` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`, the number of rows in `todos` at the time of the request. Example: three todos -> `{"count": 3}` (AC-900.1); none -> `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing `DatabaseUnavailable` handling, unchanged).

Unchanged, and asserted by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` -> `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` -> `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their status codes and bodies.

## Data

No schema change; `count(*)` over the existing `todos` table.
