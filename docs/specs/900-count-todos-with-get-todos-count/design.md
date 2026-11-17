# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint's whole purpose is to avoid moving every row (Problem). No index or schema change is needed (non-goal).
- Only a `GET` route is added for the literal path `/todos/count`. `PATCH` and `DELETE` on `/todos/count` keep falling through to the existing `/{todo_id}` routes, where `parse_id("count")` is `None` and they answer the existing `todo_not_found` 404 (AC-900.2). No `PATCH`/`DELETE` handler is registered for `/count`, because that would answer `405` instead.
- The handler uses the existing `request.app.state.db.run(...)` path, so an unreachable database answers the existing `503 unavailable` like every other endpoint.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `@router.get("/count")` → `{"count": n}` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": int}` where `count` is the number of rows in `todos`, `>= 0` (AC-900.1: three todos → `{"count": 3}`; AC-900.2: none → `{"count": 0}`).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing behaviour of every todos endpoint).

Unchanged, and asserted by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` behave exactly as before.

## Data

No change: reads the existing `todos` table.
