# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with one `SELECT count(*) FROM todos`, not by loading the list and taking `len()`: avoiding the transfer of the whole list is the point of the feature (Problem). No index or schema change is needed (non-goal: no schema change).
- The route is a static path `GET /todos/count` on the existing `/todos` router. There is no `GET /todos/{id}` route, so nothing can shadow it for GET. For `PATCH` and `DELETE`, Starlette keeps looking for a full (path + method) match after a method-only mismatch, so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo`, where `parse_id("count")` fails and they answer `404 todo_not_found` exactly as for any non-UUID id (AC-900.2). The handler is declared before the `/{todo_id}` routes anyway, so a future `GET /todos/{id}` would not shadow it.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of rows in `todos` at the time of the query, a non-negative integer, no other fields (AC-900.1: three todos → `{"count": 3}`; AC-900.2: none → `{"count": 0}`).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable within the deadline, as for every other `/todos` endpoint (existing `db.run` behaviour, unchanged).
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). An invalid body keeps the existing `parse_patch` behaviour (body is validated before the id), unchanged.
  - `DELETE /todos/count` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2).
  - `POST /todos/count`, `PUT /todos/count` → `405` `{"error": {"code": "method_not_allowed", "message": "Method not allowed"}}` (existing generic handler; not a criterion, stated for completeness).

All existing endpoints (`GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`) keep their contract (AC-900.2).

## Data

No change. Query: `SELECT count(*) FROM todos`, read with a plain cursor; the result is converted to `int`.

## Risks

- `count(*)` is a sequential scan on a large table; acceptable for a todo list and out of scope to optimise (non-goal: no schema change).
