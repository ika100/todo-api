# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`, not by loading the list: the endpoint exists to avoid transferring the rows (Problem), and a full scan of a single-column count is the cheapest exact answer without a schema change (non-goal: no schema change).
- Only a `GET /todos/count` route is added. `PATCH` and `DELETE` on `/todos/count` keep matching the existing `/{todo_id}` routes, where `parse_id("count")` fails and the routes already answer `404 todo_not_found` (AC-900.2). No handler for those methods is added on `/count`, so the id routes are not shadowed. There is no `GET /todos/{todo_id}` route, so route order cannot shadow anything.
- The query goes through `app.state.db.run(...)` like every other route, so an unreachable database answers the existing `503 unavailable` body within the existing deadline. No new behaviour.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`: the number of rows in `todos` at the time of the request. Exactly one key. Three todos give `{"count": 3}` (AC-900.1); none give `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached (existing behaviour of every todo route).

Unchanged, stated because AC-900.2 depends on it:

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` do not change.

Signatures:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...  # JSONResponse({"count": n})
```

## Data

No change. Reads table `todos`.
