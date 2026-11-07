# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, never by loading the list: the endpoint exists to avoid transferring every row (Problem).
- The route is registered for `GET` only, on the existing `/todos` router. Starlette treats a path match with the wrong method as a partial match and keeps looking for a full one, so `PATCH /todos/count` and `DELETE /todos/count` still reach `/{todo_id}`. `parse_id("count")` returns `None` there, and the caller gets the existing `404 todo_not_found` (AC-900.2). No change to the id routes.
- Registration order: `GET /count` is declared before the `/{todo_id}` routes. There is no `GET /{todo_id}` today, so order is not needed for correctness yet. It keeps the route correct if one is added later.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` takes no query parameters or body.

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`. The body has exactly one key, `count`, a JSON integer (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable. This comes from the existing `DatabaseUnavailable` handler.

These stay unchanged (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` returns `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` returns the same `404 todo_not_found` body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their current behavior.

## Data

No schema change. The query is `SELECT count(*) FROM todos`.

## Risks

- `count(*)` is a sequential scan on large tables. That is acceptable at todo-list scale, and the spec puts no latency target on it.
