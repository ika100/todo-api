# Design — 900 Count the todos with GET /todos/count

Builds on [001's design](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002's design](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid; this adds one read-only route.

## Decisions

- **Count in the database with `SELECT count(*) FROM todos`**, not by loading the list and calling `len()`: the point of the endpoint is to avoid moving every row (Problem). One new repository function, `count_todos`, run through `Database.run` like every other query, so the 2.5 s deadline and the `503 unavailable` mapping apply unchanged.
- **A static route `GET /todos/count` on the existing `/todos` router.** There is no `GET /todos/{id}`, so nothing can shadow it or be shadowed by it. `PATCH /todos/count` and `DELETE /todos/count` keep reaching `patch_todo` / `delete_todo`: Starlette treats the `GET /count` route as a partial (method-mismatch) match and keeps looking for a full match, which the `/{todo_id}` routes provide. `parse_id("count")` returns `None`, so both answer `404 todo_not_found` exactly as for any non-UUID id (AC-900.2). No change to the id routes is needed or allowed.
- **No ADR**: every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list mentions `GET /todos/count` and links spec 900 | changed |

Key signatures (types only):

```python
# todos/repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos


# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...  # {"count": n}
```

## Contract

### `GET /todos/count`

| Condition | Response | Criteria |
|---|---|---|
| database answers | `200`, `Content-Type: application/json`, body exactly `{"count": <int>}` where `<int>` is the number of rows in `todos` (a JSON integer, `>= 0`, no other keys) | AC-900.1, AC-900.2 |
| database unreachable or slower than 2.5 s | `503 unavailable` (001's error body and message) | inherited from 001 |

- No query parameters are read; any given are ignored (filtering is a non-goal).
- The request body, if any, is ignored.
- The count includes done and open todos alike.

### Unchanged routes (AC-900.2)

- `PATCH /todos/count` with a valid body (e.g. `{"done": true}`) → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, without database access. With an invalid body, 002's rule order still applies (body rules first), so it answers `422` as for any id.
- `DELETE /todos/count` → the same `404 todo_not_found` body, without database access.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, the probes and `/metrics` behave exactly as before.

### Test harness

No new fixtures. Acceptance tests go in a new file (e.g. `tests/test_todos_count.py`) and use the existing `client` fixture from `tests/conftest.py` (fresh `todos` table per test). Create todos with `POST /todos`. `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are not modified.

## Data

No change. Table `todos`, its CHECK and index stay as in 001. No migration, no new configuration, no gitops change (non-goals).
