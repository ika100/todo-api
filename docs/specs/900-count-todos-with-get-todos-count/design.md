# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists to avoid transferring every row (Problem), so the service should not do that internally either.
- The route is registered for `GET` only on the existing `/todos` router. Because no `GET /todos/{todo_id}` route exists, Starlette treats `PATCH`/`DELETE /todos/count` as a partial match on the count route and keeps looking; the full match is the existing `/{todo_id}` routes, where `parse_id("count")` fails and `todo_not_found` is raised (AC-900.2). No change to the id routes or to `parse_id` is needed. Declare the count route before the `/{todo_id}` routes anyway, so a later `GET /{todo_id}` cannot shadow it.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`; exactly one key (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable (existing `DatabaseUnavailable` handling via `app.state.db.run`).

Unchanged, and now explicitly guaranteed for the literal id `count` (AC-900.2):

- `PATCH /todos/count` with a valid body (e.g. `{"done": true}`) → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` behave as before.

## Data

No schema change. Query: `SELECT count(*) FROM todos`.

## Risks

- `count(*)` is a sequential scan on large tables; acceptable at this service's scale, no index or caching.
