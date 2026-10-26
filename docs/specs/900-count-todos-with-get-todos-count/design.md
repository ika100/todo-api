# Design — 900 Count the todos with GET /todos/count

Builds on the designs of [001](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid. This design only adds one read endpoint.

## Decisions

- **Count in the database with `SELECT count(*) FROM todos`.** The router does not load the list and count it in Python. That would undo the point of the endpoint (AC-900.1). One new repository function, `count_todos(conn) -> int`, sits next to `list_todos` and goes through `Database.run` like every other query. So the 2.5 s deadline and the `503 unavailable` mapping apply unchanged.
- **A static `GET /count` route on the existing `/todos` router, declared before the `{todo_id}` routes.** No `GET /todos/{id}` route exists, so `GET /todos/count` cannot collide with an id route. Declaring it first keeps that true if one is added later. `PATCH /todos/count` and `DELETE /todos/count` still reach the existing id handlers. `parse_id("count")` returns `None`, so they answer `404 todo_not_found` without touching the database, exactly as for any non-UUID id (AC-900.2). This needs no code change and must stay that way: do not add PATCH or DELETE handlers for `/count`.
- **No ADR.** The decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler, declared before the `{todo_id}` routes | changed |
| `README.md` | endpoint list gets the `GET /todos/count` line | changed |

Key signatures (types only):

```python
# todos/repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos

# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...
```

## Contract

### `GET /todos/count` (new)

- `200`, `Content-Type: application/json`, body exactly `{"count": <int>}`. `count` is a JSON integer ≥ 0 (never a string or a float), and it equals the number of todos `GET /todos` would return at that moment. Done and open todos both count (AC-900.1, AC-900.2).
- No query parameters are read. Unknown query parameters are ignored (filtering and paging are non-goals).
- Database unreachable or slower than 2.5 s → `503` with `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`, as for the other endpoints.

### Unchanged endpoints (AC-900.2)

- `PATCH /todos/count` with body `{"done": true}` → `404` with `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. This is the same as for any non-UUID id. Body validation still runs first (002 rule order), so an invalid body still answers `422`.
- `DELETE /todos/count` → `404` with the same `todo_not_found` body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, the probes, the serialization and the error format do not change.

### Test harness

No new fixtures. The acceptance tests go in a new file (for example `tests/test_todos_count.py`) and use the existing `client` fixture from `tests/conftest.py`. They create todos through `POST /todos`. `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are not modified.

## Data

No change. No migration, and no new index: `count(*)` on the `todos` table is fine at this service's size.

## Risks

- **Count and list are not one snapshot.** A count and a following `GET /todos` can differ if a write lands between them. This is accepted: each request is consistent on its own.
