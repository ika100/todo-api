# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is a `SELECT count(*) FROM todos` in the repository, run through the existing `db.run` (same deadline, rollback and `503` mapping as every other route). Counting in Python after `list_todos` would download the rows the spec wants to avoid.
- `GET /todos/count` is a GET-only static route on the existing `/todos` router, declared before the `/{todo_id}` routes. There is no `GET /todos/{todo_id}` route, so nothing can shadow it. `PATCH` and `DELETE /todos/count` keep reaching the id routes, where `parse_id("count")` returns `None` and they answer `404 todo_not_found` (AC-900.2). The new route must not register any other method, because a `PATCH`/`DELETE` handler on `/count` would shadow the id routes.
- No ADR: every choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query parameters are ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: the number of rows in `todos` at the time of the query. Exactly one key. (AC-900.1, AC-900.2)
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable, as for `GET /todos`.
- Other methods on `/todos/count`: `PATCH` with a valid body and `DELETE` answer `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, identical to any unknown id (AC-900.2). `PATCH` with an invalid body answers its validation error first, as for any id (unchanged behaviour). `POST /todos/count` and `PUT /todos/count` answer `405` `method_not_allowed`, as they do today.

Existing endpoints are unchanged (AC-900.2).

## Data

No schema change. Query: `SELECT count(*) FROM todos` (bound-parameter free, no user input).
