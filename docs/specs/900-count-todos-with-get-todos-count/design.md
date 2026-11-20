# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list and counting it in Python: avoiding the full read is the point of the feature (Problem).
- The route is a static `GET /count` on the existing `/todos` router. No `GET /todos/{todo_id}` exists, and Starlette prefers a full (path + method) match over a path-only match, so `PATCH /todos/count` and `DELETE /todos/count` still reach the id handlers. `parse_id("count")` returns `None` and they answer `404 todo_not_found` exactly as for any unknown id (AC-900.2). The route order in `router.py` therefore does not matter; place it after `list_todos` for readability.
- No new module, dependency, configuration, schema change or ADR: the feature is local and extends the existing repository/router pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler: `count = await request.app.state.db.run(repository.count_todos)`; returns `JSONResponse({"count": count})` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: the number of rows in `todos` at the time of the request. Exactly one key. Three todos give `{"count": 3}` (AC-900.1); none give `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached, the same as every other `/todos` endpoint (via `db.run` and the existing `DatabaseUnavailable` handler).
- Query parameters are ignored (no filtering, no paging: non-goal).

Unchanged, and now explicitly part of this spec (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- Other methods on `/todos/count` (e.g. `POST`, `PUT`) → `405` `{"error": {"code": "method_not_allowed", "message": "Method not allowed"}}`, as the framework answers today for an id path. Not a criterion; stated so testers do not guess.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their current contract.

## Data

No schema change. Reads the existing `todos` table.
