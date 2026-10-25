# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in Postgres with `SELECT count(*) FROM todos`, not by loading the list: the point of the endpoint is to avoid materialising every row (spec Problem).
- The route is a static `GET` path on the existing `/todos` router, with no new module. The router has no `GET /{todo_id}`, so the static path cannot collide with a GET id route. `PATCH` and `DELETE` keep their `/{todo_id}` routes. Starlette treats a path match with the wrong method as a partial match and keeps searching, so `PATCH /todos/count` and `DELETE /todos/count` still reach the id handlers. Those handlers reject `"count"` in `parse_id` and answer `todo_not_found` (AC-900.2). The count route is declared before the id routes anyway, so a later `GET /{todo_id}` cannot shadow it.
- Errors follow the existing paths: a database that cannot be reached answers `503 unavailable` through `Database.run`, the same as every other `/todos` endpoint.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`. `count` is a JSON integer, never a string, and is the only key. Three todos give `{"count": 3}` (AC-900.1). No todos, including a fresh database with no table rows, give `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing behaviour of every `/todos` route).

Unchanged id routes, for the literal id `count` (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.

Other methods on `/todos/count` (`POST`, `PUT`) behave as they did before this feature. They are outside the criteria.

`GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` do not change.

## Data

No schema change. `count(*)` on `todos`; the table is small and the query needs no new index.

## Risks

- Route order: declaring `GET /count` after a future `GET /{todo_id}` would shadow it. The route goes first in the router, and the AC-900 tests catch a regression.
