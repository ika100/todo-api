# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists so that nothing has to fetch every row (spec Problem).
- Only `GET /todos/count` is added. The id routes `PATCH /todos/{todo_id}` and `DELETE /todos/{todo_id}` stay as they are: `count` is not a UUID, so `parse_id` returns `None` and they already answer `404 todo_not_found` (AC-900.2). Do not add PATCH/DELETE handlers for `/count`.
- No `GET /todos/{todo_id}` route exists, so the order of route declarations does not matter. Declare the new route right after `list_todos` anyway, so that a later GET-by-id cannot shadow it.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |

## Contract

`GET /todos/count` (no query parameters, no body):

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`; exactly the one key `count`, an integer, never a string (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable, the same as every other `/todos` route (existing `DatabaseUnavailable` handler via `app.state.db.run`).
- Any other method on `/todos/count`: unchanged behaviour. `PATCH /todos/count` with a valid body and `DELETE /todos/count` answer `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2).

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

No schema change (spec Non-goals).
