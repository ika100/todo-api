# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` run through the existing `db.run` (same deadline, same `503 unavailable` mapping as `GET /todos`). Loading the list and counting it in Python would defeat the point of the endpoint (AC-900.1).
- Only a `GET` route is added at `/todos/count`. There is no `GET /todos/{id}`, so nothing can shadow it. `PATCH` and `DELETE` on `/todos/count` keep reaching the existing `/{todo_id}` routes: Starlette prefers a route whose path and method both match over a path-only match, and `parse_id("count")` returns `None`, so both answer `404 todo_not_found` exactly as for any other non-UUID id (AC-900.2). No change to those handlers.
- No ADR: every decision stays inside this feature. No schema, configuration or gitops change (spec non-goals).

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list gains the new line and a link to spec 900 | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query parameters are ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`, where `count` is a JSON integer >= 0: the number of rows in `todos` at the time of the query (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached within the existing deadline (unchanged behaviour of `db.run`, same as `GET /todos`).
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body (e.g. `{"done": true}`) → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). An invalid body still answers `422 invalid_request` first, as for any id (body is parsed before the id, unchanged).
  - `DELETE /todos/count` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2).
  - `POST /todos/count` / `PUT /todos/count` → `405` `{"error": {"code": "method_not_allowed", "message": "Method not allowed"}}` (existing generic handler; not a criterion).

All other endpoints are unchanged (AC-900.2).

Pseudocode:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()
    return int(row[0]) if row is not None else 0

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No change: reads the existing `todos` table.
