# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is a `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: the endpoint exists so that nobody loads every row to count them (Problem).
- `GET /todos/count` is a static route on the existing `/todos` router. No `GET /todos/{id}` route exists, so the GET cannot collide with an id route. For `PATCH`/`DELETE /todos/count`, Starlette treats the GET-only `/count` route as a partial match only (path matches, method does not) and keeps looking, so the existing `/{todo_id}` routes still handle them; `parse_id("count")` returns `None` and they answer the existing `404 todo_not_found` (AC-900.2). Do not add any handling for `count` to the id routes.
- No ADR: this is a feature-local endpoint that follows the existing router and repository pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: the number of rows in `todos` (AC-900.1, AC-900.2). The body has exactly one key, `count`.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached, the same as every other `/todos` endpoint (through `db.run` and the existing `DatabaseUnavailable` handler).

Unchanged, because the id routes keep handling these (AC-900.2):

- `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.

All other endpoints keep their contract from specs 001 and 002.

## Data

No schema change. Query: `SELECT count(*) FROM todos`.
