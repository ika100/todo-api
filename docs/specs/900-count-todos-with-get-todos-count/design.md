# Design — 900 Count the todos with GET /todos/count

Builds on [001's design](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002's design](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid. The only changes are listed here.

## Decisions

- **A `GET /todos/count` route on the existing todos router, backed by one `SELECT count(*)`.** The database counts and the service never loads the rows, which is the reason for the endpoint (Problem, AC-900.1). There is no cache and no new table or index (non-goal: no schema change).
- **Only `GET` is registered on `/todos/count`. The id routes stay as they are.** There is no `GET /todos/{id}`, so a static `GET /todos/count` cannot collide with an id route. `PATCH /todos/count` and `DELETE /todos/count` keep matching `/{todo_id}`. `parse_id("count")` returns `None`, so they answer `404 todo_not_found` exactly as for any unknown id (AC-900.2). PATCH keeps its rule order: body first, then id. So `{"done": true}` reaches the id check and gets the 404. Nothing needs to change for this. The task only must not add `PATCH`/`DELETE` handlers on `/count` and must not add a "count" special case to `parse_id`.
- **Errors use the existing model.** When the database is unreachable, `Database.run` raises `DatabaseUnavailable` → `503 unavailable`, the same as for `GET /todos`. No new error code.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list mentions `GET /todos/count` | changed |

Key signatures (types only):

```python
# todos/repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos

# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...  # JSONResponse({"count": n})
```

## Contract

`GET /todos/count` (no query parameters, no body; unknown query parameters are ignored)

| Case | Status | Body | Content-Type |
|---|---|---|---|
| success | `200` | `{"count": <int ≥ 0>}`, exactly one key, `count` is a JSON integer (never a string or float) | `application/json` |
| database unreachable within the deadline | `503` | `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` | `application/json` |

- Three todos → `{"count": 3}` (AC-900.1). No todos → `{"count": 0}` (AC-900.2).
- `count` counts every todo, done or not. There is no filtering (non-goal).
- `PATCH /todos/count` (any body that passes PATCH validation, e.g. `{"done": true}`) and `DELETE /todos/count` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). An invalid PATCH body still gets `422` first, unchanged from 002.
- Other methods on `/todos/count` (`POST`, `PUT`) → `405` `{"error": {"code": "method_not_allowed", "message": "Method not allowed"}}`, from the existing generic handler.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready` do not change (AC-900.2).

## Data

No change. `count(*)` on `todos`. No migration, no new index.

## Risks

- `count(*)` is a sequential or index-only scan, O(rows). The table is small for this service. If it grows large, an estimate or a counter would be a later spec.
