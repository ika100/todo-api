# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: the point of the endpoint (Problem) is to avoid reading every row.
- `GET /todos/count` is a static route on the existing `/todos` router. There is no `GET /todos/{id}` route, so nothing can shadow it or be shadowed by it. `PATCH /todos/count` and `DELETE /todos/count` keep going to the id routes, where `parse_id("count")` is `None` and the existing `404 todo_not_found` is raised (AC-900.2). No code change is needed for that part; the acceptance tests pin it.
- No ADR: every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query parameters are ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: exactly one key, the number of rows in `todos` at the time of the query (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unavailable, through the existing `db.run` deadline and `DatabaseUnavailable` handler, exactly as `GET /todos`.

Unchanged, pinned by AC-900.2:

- `PATCH /todos/count` with `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. The body is validated first, as for any id (an invalid body still answers `422 invalid_request`).
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready` do not change.

Sketch:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()   # (int,)
    return int(row[0]) if row else 0

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change, no migration (non-goal).
