# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`. Counting in the database is what lets a caller skip downloading the list (Problem), and the server should skip it too.
- Only a `GET /todos/count` route is added. There is no `PATCH`/`DELETE` route for `/count`. Starlette keeps looking for a full match after a path-only match, so `PATCH /todos/count` and `DELETE /todos/count` still reach the existing `/{todo_id}` handlers. Those handlers fail `parse_id("count")` and answer `404 todo_not_found` (AC-900.2). The route order in `router.py` does not matter for this. The count handler goes before the id handlers anyway, so a reader sees the static path first.
- There is no ADR: nothing here outlives the feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body):

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`. This is exactly one key, and the value is a JSON integer (not a string). With three todos it is `{"count": 3}` (AC-900.1). With none it is `{"count": 0}` (AC-900.2).
- `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached within the deadline. This is the same as for every existing endpoint (`db.run`).
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body, e.g. `{"done": true}`: `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
  - `DELETE /todos/count`: the same `404 todo_not_found` body.
  - Both are exactly what any non-UUID id gets (AC-900.2). `PATCH` with an invalid body answers `422 invalid_request`, as before, because the body is parsed before the id.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` do not change.

Pseudocode:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()          # (n,)
    return int(row[0]) if row else 0

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change. `count(*)` runs on the existing `todos` table.
