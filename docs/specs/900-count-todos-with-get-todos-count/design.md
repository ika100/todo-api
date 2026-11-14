# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is a `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: the point of the endpoint is to avoid reading every row (Problem).
- Only a `GET` route is added at `/todos/count`. FastAPI matches routes per method, so `PATCH /todos/count` and `DELETE /todos/count` still reach the existing `/{todo_id}` handlers, where `parse_id("count")` fails and they answer `404 todo_not_found` unchanged (AC-900.2). No guard code is needed for this; no handler other than the new one changes.
- The route is registered in the existing `todos/router.py` and runs through `app.state.db.run` like the other handlers, so a database outage answers the existing `503 unavailable` error.
- No ADR: the choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`; exactly the one key `count`, an integer equal to the number of rows in `todos` (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing behaviour of every todos route).

Unchanged, now tested for the literal id `count` (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.

`GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their contract.

## Data

No schema change. Query: `SELECT count(*) FROM todos`.
