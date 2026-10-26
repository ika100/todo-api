# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in Postgres with `SELECT count(*) FROM todos`. Loading the list and counting in Python would defeat the point of the endpoint (AC-900.1).
- The new route is a static GET route on the existing `/todos` router. No GET `/todos/{todo_id}` route exists, so `count` cannot collide with an id for GET. `PATCH` and `DELETE` on `/todos/count` keep matching the existing `/{todo_id}` routes: Starlette prefers a full match (path and method) over the partial match of the GET route, so they answer `404 todo_not_found` as they do today, because `parse_id("count")` returns `None` (AC-900.2). The count route is declared before the id routes anyway, so the intent is obvious to a reader.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`, where `count` is a non-negative JSON integer equal to the number of rows in `todos` (AC-900.1, AC-900.2). Example with no todos: `{"count": 0}`.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached within the deadline (the existing `DatabaseUnavailable` mapping, same as `GET /todos`).

Unchanged and asserted by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` behave exactly as before.

## Data

No schema change. Reads the existing `todos` table.

## Risks

- `count(*)` is a sequential scan on a large table; acceptable for a todo list, no index needed.
