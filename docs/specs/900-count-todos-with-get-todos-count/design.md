# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, run through the existing `Database.run` (same 2.5 s deadline and `503 unavailable` mapping as every other todo operation). Counting in Python after `list_todos` would defeat the purpose of the endpoint (AC-900.1).
- The route is `GET /todos/count`, registered on the existing `/todos` router. There is no `GET /todos/{id}` route, so nothing can shadow it. `PATCH` and `DELETE` keep matching `/todos/{todo_id}` only: Starlette prefers a full (path + method) match over the partial match of the GET-only `/count` route. `"count"` is not a UUID, so `parse_id` returns `None` and the handlers answer `404 todo_not_found` exactly as for any unknown id (AC-900.2). No change to the PATCH/DELETE handlers is needed.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query parameters are ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of rows in `todos`, `>= 0`. Exactly one key. Examples: three todos → `{"count": 3}` (AC-900.1); none → `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database does not answer within the deadline (existing behaviour of every todo route).
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body (e.g. `{"done": true}`) → `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). The body is validated first, as for any id (an invalid body still gives `422`, unchanged).
  - `DELETE /todos/count` → `404` with the same `todo_not_found` body (AC-900.2).
  - `POST /todos/count` → `405 method_not_allowed` (unchanged generic handler; not a criterion).

All existing endpoints (`GET/POST /todos`, `PATCH/DELETE /todos/{id}`, `/health`, `/ready`, `/ping`, `/metrics`) are unchanged.

## Data

No schema change. Query: `SELECT count(*) FROM todos`, read via `cur.fetchone()`, returned as `int`.

## Test harness

Acceptance tests use the existing `tests/conftest.py` client/database fixtures in a new test file; they create todos through `POST /todos` and assert on `GET /todos/count`.

## Risks

- `count(*)` is a sequential scan; acceptable for this service's table sizes. No index change.
