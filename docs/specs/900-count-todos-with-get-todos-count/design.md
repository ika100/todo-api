# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the point of the endpoint (Problem) is not to transfer every row.
- `GET /todos/count` is a static route on the existing `/todos` router. There is no `GET /todos/{todo_id}`, so nothing can shadow it. The router has no `PATCH /todos/count` or `DELETE /todos/count`, so those requests go to the existing id routes. `parse_id("count")` returns `None` there, and the existing `todo_not_found` 404 follows (AC-900.2). No id route changes.
- The query goes through `app.state.db.run`, like every other route, so the existing deadline and `503 unavailable` behaviour also apply to the count.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int ≥ 0>}`. Example: three todos give `{"count": 3}` (AC-900.1), none give `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached. This is the existing behaviour of every `/todos` route.

Unchanged, and asserted by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` behave exactly as before.

## Data

No schema change. The query is `SELECT count(*) FROM todos`.
