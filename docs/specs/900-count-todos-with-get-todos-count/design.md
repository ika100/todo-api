# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: the point of the endpoint is to avoid loading every row (Problem).
- `GET /todos/count` is a static route on the existing `/todos` router. There is no `GET /todos/{id}` route, so nothing shadows it on GET; `PATCH` and `DELETE /todos/count` still reach the existing `/{todo_id}` routes, where `parse_id("count")` returns `None` and the existing `404 todo_not_found` is answered (AC-900.2). No route or validation change is needed for that.
- No ADR: every choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int ≥ 0>}`: the number of rows in `todos` (AC-900.1, AC-900.2). `count` is a JSON integer, never a string. No other field.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable, exactly as for `GET /todos` (existing `DatabaseUnavailable` mapping).

Unchanged and confirmed by AC-900.2:

- `PATCH /todos/count` with `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`: no change.

Pseudocode:

```python
async def count_todos(conn) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()
    return int(row[0]) if row else 0

@router.get("/count")
async def count_todos(request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change, no migration, no configuration change.
