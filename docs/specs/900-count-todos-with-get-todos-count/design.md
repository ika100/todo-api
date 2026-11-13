# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists to avoid moving the list (AC-900.1).
- Only a `GET` route is added at `/todos/count`. `PATCH` and `DELETE` on that path keep matching the existing `/{todo_id}` routes, where `parse_id("count")` returns `None` and the handler raises the existing `todo_not_found` error, so no special-casing is needed (AC-900.2).
- The route follows the existing pattern: handler in `todos/router.py`, query in `todos/repository.py`, run through `request.app.state.db.run`, so a database outage answers the existing `503 unavailable` error like every other endpoint.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}` — the number of rows in `todos` at the time of the request (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing behaviour of all `/todos` routes).

Unchanged and asserted by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` are unchanged.

## Data

No schema change; reads the existing `todos` table.
