# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in Postgres (`SELECT count(*) FROM todos`) by a new `repository.count_todos`, not by loading the list and taking `len()`: the point of the endpoint is to avoid moving every row (Problem). It runs through `Database.run` like every other query, so the deadline and `503` mapping of spec 001 apply unchanged.
- `GET /todos/count` is a plain `@router.get("/count")` on the existing `/todos` router, declared before the `/{todo_id}` routes. No `PATCH` or `DELETE` handler is added on `/count`: Starlette prefers a route whose path and method both match over one whose path matches only, so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo`, where `parse_id("count")` is `None` and they answer `404 todo_not_found` exactly as for any unknown id (AC-900.2). There is no `GET /todos/{id}` route, so nothing can shadow or be shadowed on `GET`.
- No ADR: every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` route | changed |
| `README.md` | API list gains the new endpoint | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query parameters are ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}` where `count` is a JSON integer >= 0, the number of rows in `todos` at the time of the query (AC-900.1, AC-900.2). No other fields.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot answer within the existing deadline, identical to `GET /todos` (spec 001).
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body (for example `{"done": true}`) → `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). With an invalid body it answers `422` exactly as `PATCH /todos/<any-non-uuid>` does today, because body parsing precedes the id check (spec 002 rule order, unchanged).
  - `DELETE /todos/count` → `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2).
  - `POST /todos/count` and `PUT /todos/count` → `405 {"error": {"code": "method_not_allowed", "message": "Method not allowed"}}` (existing generic handler; not a criterion).
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` do not change (AC-900.2).

Sketch:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()
    return int(row[0]) if row else 0

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change, no migration, no new configuration, no new dependency.
