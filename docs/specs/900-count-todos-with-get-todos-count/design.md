# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: it saves the transfer the spec exists to avoid (Problem). Feature-local, no ADR.
- `GET /todos/count` is a static route on the existing `/todos` router, declared before the id routes. There is no `GET /todos/{id}`, so nothing can shadow it on GET. For `PATCH` and `DELETE`, Starlette prefers a full match (path and method) over a partial one, so `/todos/count` keeps reaching `patch_todo` / `delete_todo`, where `parse_id("count")` is `None` and the existing `404 todo_not_found` answers (AC-900.2). No change to those handlers.
- No response model and no new error: the body is built with `JSONResponse` like the other `/todos` routes, which sets `Content-Type: application/json` (AC-900.1).

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `todos/repository.py` | `count_todos(conn) -> int` | changed |
| `todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of rows in `todos`, `>= 0`. Three todos → `{"count": 3}` (AC-900.1); none → `{"count": 0}` (AC-900.2). No other fields.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database misses the deadline, as for every `/todos` route (existing `db.run` behaviour).

Unchanged and verified by AC-900.2:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` behave exactly as before.

Other methods on `/todos/count` (`POST`, `PUT`) keep whatever they answer today. The spec does not cover them, and this design does not change them.

## Data

No schema change. Query: `SELECT count(*) FROM todos`, no parameters.
