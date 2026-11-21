# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`: the point of the endpoint is to avoid reading every row (Problem).
- `GET /todos/count` is a literal route on the existing `/todos` router, declared before the `/{todo_id}` routes. Only `GET` is registered on `/count`, so `PATCH`/`DELETE /todos/count` keep matching `/{todo_id}`, where `parse_id("count")` fails and the existing `todo_not_found` 404 is raised (AC-900.2). No `GET /todos/{todo_id}` route exists, so no shadowing question arises for `GET`.
- No ADR: a feature-local route on an existing pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}` — the number of rows in `todos` at query time (AC-900.1, AC-900.2). Exactly one key.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable, the same path every other `/todos` endpoint uses (`db.run` raises `DatabaseUnavailable`).
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body (`{"done": true}`) → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2).
  - `DELETE /todos/count` → `404`, same body (AC-900.2).
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` are unchanged.

Pseudocode:

```
repository.count_todos(conn) -> int:
    SELECT count(*) FROM todos  -> fetchone()[0]

@router.get("/count")   # placed above the /{todo_id} routes
async def count_todos(request) -> JSONResponse:
    n = await request.app.state.db.run(repository.count_todos)
    return JSONResponse({"count": n})
```

## Data

No schema change (non-goal).
