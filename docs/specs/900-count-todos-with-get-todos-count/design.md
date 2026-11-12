# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count comes from the database as `SELECT count(*) FROM todos`, not from `len(list_todos())`, because the point of the endpoint is to avoid reading every row (Problem).
- `GET /todos/count` is a GET-only route on the existing `/todos` router, placed before the `/{todo_id}` routes. No `GET /todos/{todo_id}` exists, so the GET does not collide with anything. `PATCH` and `DELETE /todos/count` only partially match the new route (wrong method). Starlette keeps looking for a full match and finds `/{todo_id}`. There `parse_id("count")` returns `None` and the handler raises the existing `todo_not_found`, so the response is a 404 and not a 405 (AC-900.2).
- No new module, no ADR. This is one more query and one more route in the existing pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos(request) -> JSONResponse` | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": int}`, where `count` >= 0 is the number of rows in `todos` (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable (existing `DatabaseUnavailable` handling, unchanged).

Unchanged and asserted by AC-900.2:

- `PATCH /todos/count` with `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their current behavior.

Pseudocode:

```
repository.count_todos(conn) -> int:
    row = (await conn.execute("SELECT count(*) FROM todos")).fetchone()
    return int(row[0])

@router.get("/count")
async def count_todos(request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change.
