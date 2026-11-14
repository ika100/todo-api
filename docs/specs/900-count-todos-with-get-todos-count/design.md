# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the point of the endpoint is to avoid transferring every row (Problem).
- The route is a literal `GET /count` on the existing `/todos` router. There is no `GET /todos/{todo_id}`, so it shadows nothing; `PATCH /todos/{todo_id}` and `DELETE /todos/{todo_id}` stay untouched and keep answering `404 todo_not_found` for `count`, because `parse_id("count")` is `None` (AC-900.2).
- No new dependency, configuration, schema or gitops change (Non-goals). No ADR: the choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: the number of rows in `todos` at the time of the request; exactly one key (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing `DatabaseUnavailable` handling, same as `GET /todos`).

Unchanged (AC-900.2):

- `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` keep their current contract.

Pseudocode:

```python
async def count_todos(conn) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()
    return int(row[0])

@router.get("/count")
async def count_todos(request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change; reads the existing `todos` table.
