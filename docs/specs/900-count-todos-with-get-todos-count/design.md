# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the point of the endpoint is to avoid transferring every row (AC-900.1).
- The route is `GET /count` on the existing `/todos` router, declared before the `/{todo_id}` routes. Starlette treats a path match with the wrong method as a partial match and keeps looking, so `PATCH /todos/count` and `DELETE /todos/count` still reach the id handlers, which reject `count` as an invalid UUID with `todo_not_found` (AC-900.2). The router needs no other change.
- No ADR: this choice only affects this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` takes no query parameters and no body.

- `200`, `Content-Type: application/json`, body `{"count": int}` where `count >= 0` is the number of rows in `todos` (AC-900.1, AC-900.2). Example: `{"count": 3}`.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached. This is the existing behaviour shared by every `/todos` route.

The id routes stay as they are (AC-900.2):

- `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` do not change.

Pseudocode:

```python
async def count_todos(conn) -> int:
    row = await (await conn.execute("SELECT count(*) FROM todos")).fetchone()
    return int(row[0])

@router.get("/count")
async def count_todos(request) -> JSONResponse:
    return JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})
```

## Data

No schema change.
