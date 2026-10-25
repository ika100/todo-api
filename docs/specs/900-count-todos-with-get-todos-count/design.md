# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list and taking `len()`: that is the point of the endpoint (AC-900.1). No index or schema change is needed (non-goal: no schema change).
- The route is a literal `GET /todos/count` on the existing `todos` router. There is no `GET /todos/{todo_id}` route, so nothing is shadowed for GET. `PATCH` and `DELETE /todos/count` keep falling through to the existing `/{todo_id}` routes: Starlette only partially matches the `GET`-only `/count` route for other methods and prefers the full `/{todo_id}` match, where `parse_id("count")` returns `None` and the handler raises the existing `todo_not_found` (AC-900.2). No change to the PATCH or DELETE handlers.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}` — the number of rows in `todos`. Exactly one key. Example: three todos → `{"count": 3}` (AC-900.1); none → `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing `DatabaseUnavailable` handler, same as `GET /todos`).

Unchanged by this spec (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their current behaviour.

## Risks

- `count(*)` is a sequential scan on large tables; acceptable at this service's size, no paging or estimate needed (non-goal).
