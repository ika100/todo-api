# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: the point of the endpoint is to avoid reading every row (Problem). No index or schema change is needed (non-goal: schema change).
- The route is a static `GET /count` on the existing `/todos` router, declared before the `/{todo_id}` routes. There is no `GET /todos/{todo_id}`, so nothing is shadowed for GET. For `PATCH`/`DELETE /todos/count`, Starlette treats the `/count` route as a partial match only (path matches, method does not) and keeps searching; the `/{todo_id}` route is a full match and wins. `parse_id("count")` returns `None`, so both answer `404 todo_not_found` exactly as today (AC-900.2). No change to the id routes or `parse_id` is needed.
- No ADR: every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`. `count` is a JSON integer ≥ 0, the number of rows in `todos` at read time (AC-900.1: three todos → `{"count": 3}`; AC-900.2: none → `{"count": 0}`). No other fields.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database misses the deadline: the existing `db.run` / `DatabaseUnavailable` path, unchanged.
- Query parameters are ignored (non-goal: filtering, paging).

Unchanged and asserted by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → the same `404` body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`, `/metrics` keep their spec 001/002 contracts.

Other methods on `/todos/count` (`POST`, `PUT`) keep whatever the router answers today; they are not part of this spec.

## Data

No schema change. Query: `SELECT count(*) FROM todos` (parameterless), result cast to `int`.
