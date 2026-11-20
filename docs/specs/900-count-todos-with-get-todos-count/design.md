# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, run through the existing `db.run` (same deadline, rollback and `503` mapping as every other route). Counting in Python over `list_todos` would download the whole table, which is the problem the spec removes.
- The route is a static `GET /count` on the existing `/todos` router. No route shadows another: there is no `GET /todos/{id}`, and Starlette prefers a full (path and method) match over a path-only match, so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` and `delete_todo`, where `parse_id("count")` is `None` and they answer `404 todo_not_found` (AC-900.2). The count route is declared before the id routes anyway, so the order never depends on that rule.
- No ADR: every choice is local to this feature. No schema, config, dependency or gitops change (spec non-goals).

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | API list gains the new line | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query string is ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of rows in `todos`, a non-negative integer (AC-900.1: `{"count": 3}` for three todos; AC-900.2: `{"count": 0}` for none). No other fields.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached within the existing deadline, exactly as for `GET /todos`.
- `500` `{"error": {"code": "internal_error", "message": "Internal server error"}}` for unexpected failures (existing handler).

Unchanged and asserted by AC-900.2:

- `PATCH /todos/count` with `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- Every other endpoint (`GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`) keeps its spec 001/002 behaviour.

Pseudocode:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()   # (n,)
    return int(row[0])           # raise RuntimeError if row is None, like create_todo

# router.py (above patch_todo)
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No change: reads the existing `todos` table.
