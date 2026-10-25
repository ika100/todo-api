# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in Postgres with `SELECT count(*) FROM todos`, not by loading the list and counting in Python: the point of the endpoint is to avoid moving every row (AC-900.1).
- The route is registered as `GET /count` on the existing `/todos` router, and only for `GET`. Starlette tries every route: for `PATCH`/`DELETE /todos/count` the `GET /count` route matches the path but not the method (a partial match), so the router keeps looking and the full match `/{todo_id}` handles the request. `parse_id("count")` returns `None`, so the existing `todo_not_found` 404 comes back unchanged (AC-900.2). No `PATCH`/`DELETE` handler and no `405` for `/todos/count`.
- No ADR: the choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of rows in `todos`, `>= 0` (AC-900.1, AC-900.2). Example: `{"count": 3}`; empty table gives `{"count": 0}`.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable (the existing `DatabaseUnavailable` handling through `app.state.db.run`, same as `GET /todos`).

Unchanged (AC-900.2):

- `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their behaviour.

## Data

No schema change: reads the existing `todos` table.

## Risks

- `count(*)` is a sequential scan on a large table; acceptable for a todo list and still far cheaper than `GET /todos`.
