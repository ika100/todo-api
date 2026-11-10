# Design — 900 Count the todos with GET /todos/count

Builds on the designs of [001](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid. This adds one read-only route.

## Decisions

- **A static `GET` route on the existing `/todos` router, counted in SQL.** `repository.count_todos` runs `SELECT count(*) FROM todos` through `Database.run`, like `list_todos`. Counting in the database never loads rows, which is the point of the spec (AC-900.1, AC-900.2).
- **No shadowing of the id routes, by construction.** Only `GET` is added for `/todos/count`. The router has no `GET /todos/{todo_id}`, and Starlette picks a route whose path *and* method match over one whose path matches only. So `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo`, where `parse_id("count")` is `None` and they answer `404 todo_not_found` exactly as for any non-UUID id (AC-900.2). The handler is still declared above the `/{todo_id}` routes, so a later `GET /todos/{todo_id}` cannot capture `count`.
- **No migration, no config, no gitops change** (spec non-goals). No ADR: the choice is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list mentions `GET /todos/count`, link to spec 900 | changed |

```python
# todos/repository.py
async def count_todos(
    conn: AsyncConnection,
) -> int: ...  # SELECT count(*) FROM todos; bound-free, constant SQL


# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...  # 200 {"count": n}
```

## Contract

### `GET /todos/count`

| Condition | Response |
|---|---|
| database answers | `200`, `Content-Type: application/json`, body exactly `{"count": <int>}` (AC-900.1, AC-900.2) |
| database unreachable or slower than 2.5 s | `503 unavailable` (unchanged `Database.run` behaviour, as for `GET /todos`) |

- `count` is a JSON integer (not a string), `>= 0`, equal to the number of todos `GET /todos` returns at that moment, done and open todos alike. No other keys.
- Query parameters are ignored (no filtering or paging, spec non-goal). A request body is ignored.
- Other methods on `/todos/count`: `PATCH` with a valid body (`{"done": true}`) and `DELETE` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, identical to any non-UUID id, no database access (AC-900.2). `PATCH` with an invalid body keeps 002's rule order (body rules first, then `404`).
- `GET`, `POST`, `PATCH`, `DELETE` on `/todos` and `/todos/{id}`, the probes, serialization and the error body format are unchanged.

### Test harness

No new fixtures. The acceptance tests go in a new file (e.g. `tests/test_todos_count.py`) and use `tests/conftest.py`'s `client`. Create todos via `POST /todos`; start from an empty table as the existing tests do.

## Data

No change. No migration.
