# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is a single `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`. Counting in Python would load every row, which is the cost the spec removes.
- `GET /todos/count` is a static route on the existing `/todos` router. There is no `GET /todos/{id}`, so nothing else can take the GET. `PATCH` and `DELETE` keep their `/{todo_id}` routes: for the path segment `count`, `parse_id` returns `None` and they answer `404 todo_not_found` exactly as for any other id that is not a UUID (AC-900.2). The router and validation need no special case for them.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list gets `GET /todos/count` | changed |

## Contract

### `GET /todos/count`

- `200`, `Content-Type: application/json`, body `{"count": <int>}`. `count` is a JSON integer ≥ 0: the number of rows in `todos` at the time of the query (AC-900.1, AC-900.2). No other keys.
- No query parameters are read; unknown ones are ignored (no filtering, no paging: non-goals).
- Database failure or the 2.5 s deadline → `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`, through the existing `db.run` path like `GET /todos`.

### Neighbouring routes (unchanged, AC-900.2)

- `PATCH /todos/count` with a valid body (e.g. `{"done": true}`) → `404 {"error": {"code": "todo_not_found", "message": <MSG_TODO_NOT_FOUND>}}`. The body is validated first, as for any id (spec 001/002 rule order), so an invalid body still answers `422 invalid_request`.
- `DELETE /todos/count` → `404` with the same `todo_not_found` body.
- `POST /todos/count`, `PUT /todos/count` → `405 method_not_allowed`, as today for `/todos/{id}`.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`, `/ping`, `/metrics` do not change.

### Test harness

The acceptance tests use the existing `client` fixture in `tests/conftest.py` (per-test `DROP TABLE`, so "no todos" is the default state) and create todos with `POST /todos`.

## Data

No schema change. The query is `SELECT count(*) FROM todos`; psycopg returns a Python `int`.

## Risks

- `count(*)` is a sequential scan on Postgres; acceptable for a todo list and far cheaper than serializing the list.
