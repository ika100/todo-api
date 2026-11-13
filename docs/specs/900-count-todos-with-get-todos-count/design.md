# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count comes from one `SELECT count(*) FROM todos` in the repository, run through the existing `db.run` (same 2.5 s deadline, same `503 unavailable` mapping). The handler does not load the list and call `len()`, because that defeats the purpose of the endpoint (Problem).
- No route reordering is needed. The router has no `GET /todos/{id}`, so the new literal `GET /count` cannot shadow an id route, and no id route can shadow it. For `PATCH`/`DELETE /todos/count`, Starlette picks the full method match (`/{todo_id}`) over the partial match (`GET /count`). `parse_id("count")` returns `None`, which already answers `404 todo_not_found` (AC-900.2). The existing handlers do not change.
- There is no ADR. The endpoint is local to this feature and follows the existing router and repository pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count`
- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`. `count` is the number of rows in `todos`, for example `{"count": 3}` (AC-900.1) or `{"count": 0}` (AC-900.2). It has no query parameters. Any query string is ignored (filtering is a non-goal).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database misses the deadline. This is the existing behaviour of every `/todos` route.

Unchanged, pinned by AC-900.2:
- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their spec 001/002 contracts.

## Data

No schema change. Query: `SELECT count(*) FROM todos`. It has no parameters, and the result is read as `int`.
