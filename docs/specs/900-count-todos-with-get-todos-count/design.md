# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in Postgres with `SELECT count(*) FROM todos`, not by loading the list and calling `len()`: the point of the endpoint is to avoid moving every row (Problem). No index, schema or migration change.
- The route is a static `GET` route registered in the existing `/todos` router, above the `/{todo_id}` routes. Starlette prefers a full (path and method) match, so `PATCH /todos/count` and `DELETE /todos/count` keep reaching the id handlers, where `parse_id("count")` is `None` and they answer `404 todo_not_found` like any other non-UUID id (AC-900.2). There is no `GET /todos/{id}`, so the new route shadows nothing.
- No ADR: every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query parameters are ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: `count` is a non-negative JSON integer, the number of rows in `todos` at the time of the query (AC-900.1, AC-900.2). Exactly one key.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database does not answer within the existing 2.5 s deadline (same path as every other endpoint, via `Database.run`).

Unchanged, and binding for AC-900.2:

- `PATCH /todos/count` with `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their spec 001/002 contracts.

## Data

No change. Query: `SELECT count(*) FROM todos` (bound by nothing, no parameters).

## Risks

- `count(*)` is a sequential scan on large tables; acceptable for a todo list, and still far cheaper than `GET /todos`.
