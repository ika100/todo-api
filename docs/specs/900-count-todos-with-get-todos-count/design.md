# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, run through the existing `Database.run` (same deadline, same `503 unavailable` mapping as every other todo route). Counting in SQL instead of `len(list_todos())` is the point of the feature: no rows are transferred.
- The route is a plain `@router.get("/count")` on the existing `/todos` router. Nothing else routes on `GET`, so nothing shadows it. `PATCH` and `DELETE` on `/todos/count` keep reaching the id handlers: Starlette returns on the first route that matches path **and** method (`Match.FULL`), and the `GET /count` route only matches the path (`Match.PARTIAL`), which is used only when no route matches fully. `PATCH /{todo_id}` and `DELETE /{todo_id}` match fully, `parse_id("count")` returns `None`, and they answer `404 todo_not_found` exactly as for any unknown id (AC-900.2). For this reason the new route must not be registered with extra methods (`api_route(..., methods=[...])`) or as a catch-all.
- No ADR: the choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

**`GET /todos/count`** (new) — no query parameters, no body.

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of todos that exist, done or not. `{"count": 0}` when there are none (AC-900.1, AC-900.2). `count` is a JSON integer (never a string or float); the object has no other keys.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database does not answer within the existing deadline (unchanged behaviour of every todo route).
- Query parameters are ignored (no filtering, no paging: non-goals).

**`PATCH /todos/count`** and **`DELETE /todos/count`** (unchanged handlers) — `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, identical to any other non-UUID id. For `PATCH`, body validation runs first as today, so an invalid body still answers `422` before the id is checked; with a valid body (`{"done": true}`) the answer is `404` (AC-900.2).

`GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`, `/metrics` do not change (AC-900.2).

Pseudocode:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int:
    cur = await conn.execute("SELECT count(*) FROM todos")
    row = await cur.fetchone()  # count(*) always yields one row
    return int(row[0])


# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse:
    count = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": count})
```

## Data

No schema change, no migration, no new configuration (non-goal).
