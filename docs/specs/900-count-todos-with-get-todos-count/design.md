# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists to avoid transferring every row (Problem), and that also applies between the service and Postgres.
- `GET /todos/count` is a new literal route on the existing `/todos` router. The router has no `GET /todos/{todo_id}`, so nothing can shadow it, and `PATCH`/`DELETE /todos/{todo_id}` remain the only routes matching `/todos/count` for those methods. `"count"` is not a UUID, so `parse_id` returns `None` and they answer the existing `404 todo_not_found` unchanged (AC-900.2). No change to the id routes is needed.
- The handler goes through `request.app.state.db.run(...)` like every other route, so an unreachable database answers the existing `503 unavailable` within the existing deadline. No new error code.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`, the number of rows in `todos` at the time of the query. Exactly one key. AC-900.1 (`{"count": 3}` for three todos), AC-900.2 (`{"count": 0}` for none).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable (existing behaviour of every `/todos` route).

Unchanged, now asserted for the literal id `count` (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.

All other endpoints (`GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`) do not change.

Signatures:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int: ...   # SELECT count(*) FROM todos

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...  # JSONResponse({"count": n})
```

## Data

No schema change (non-goal). Reads the existing `todos` table.
