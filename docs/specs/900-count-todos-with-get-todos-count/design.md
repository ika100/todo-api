# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists to avoid transferring every row (Problem), and that also applies between the service and Postgres.
- The route is a literal `GET /todos/count` on the existing `/todos` router. No `GET /todos/{todo_id}` route exists, so nothing shadows it. `PATCH /todos/count` and `DELETE /todos/count` keep going to the existing id routes. `parse_id("count")` returns `None`, so they answer `404 todo_not_found` as for any unknown id (AC-900.2). No change to those handlers.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int`: a single `SELECT count(*) FROM todos` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler that runs `count_todos` through `request.app.state.db.run` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of stored todos, `>= 0`. The body has no other fields (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached. This is the existing `DatabaseUnavailable` handling, unchanged.

Unchanged and still binding (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` returns `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` returns `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` behave as before.

## Data

No schema change. `count(*)` on `todos` returns a Postgres `bigint`. The handler returns it as a JSON integer.

## Risks

- `count(*)` scans the whole table. That is fine for this service's size, and the spec excludes filtering and paging.
