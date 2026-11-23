# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is a `SELECT count(*) FROM todos` in the repository, run through the existing `db.run` deadline wrapper like every other query, so an unreachable database answers the existing `503 unavailable` (AC-900.1, AC-900.2).
- Only a `GET` route on `/todos/count` is added. There is no `GET /todos/{todo_id}`, so nothing can shadow it; `PATCH` and `DELETE /todos/count` keep falling through to the id routes, where `parse_id("count")` fails and they answer `404 todo_not_found` unchanged (AC-900.2). No route-ordering trick and no reserved-id check is needed.
- No schema, config or gitops change (non-goal).

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `@router.get("/count")` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: the number of rows in `todos` (AC-900.1: three todos → `{"count": 3}`; AC-900.2: none → `{"count": 0}`).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable (existing behaviour of every `/todos` route).

Unchanged, stated because AC-900.2 tests it:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` do not change.

Pseudocode:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()
    return int(row[0]) if row else 0

# router.py
@router.get("/count")
async def get_todo_count(request: Request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```
