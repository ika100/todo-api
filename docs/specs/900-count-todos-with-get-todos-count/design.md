# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, run through `app.state.db.run` like every other query. It inherits the existing 2.5 s deadline and the `503 unavailable` mapping without new code. Counting in Python after `list_todos` would download the very rows this endpoint exists to avoid (Problem).
- The route is `GET` only, registered on the existing `/todos` router as `@router.get("/count")`. There is no `GET /todos/{id}` route, so nothing can shadow it. Starlette treats a path match with the wrong method as a partial match and keeps looking. `PATCH /todos/count` and `DELETE /todos/count` therefore still reach `/{todo_id}`, where `parse_id("count")` returns `None` and the handlers answer `404 todo_not_found` (AC-900.2). The router needs no special case for `count`.
- There is no ADR, because every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count`, no query parameters and no body.

- `200`, `Content-Type: application/json`, body `{"count": <int ≥ 0>}`. `count` is a JSON integer, never a string, and it is the number of rows in `todos` (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database misses the deadline. This is the existing behaviour of every todos route.

Unchanged by this spec (AC-900.2):

- `PATCH /todos/count` with `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404`, with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their spec 001/002 contract.
- `POST /todos/count` is not part of the spec. It answers whatever the router produces for a path that matches only with other methods (`405 method_not_allowed`), and this feature does not test it.

Sketch:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()
    return int(row[0]) if row else 0

# router.py
@router.get("/count")
async def count_todos_route(request: Request) -> JSONResponse:
    return JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})
```

## Data

There is no schema change and no migration (Non-goals).
