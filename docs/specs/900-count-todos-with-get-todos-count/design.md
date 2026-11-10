# Design — 900 Count the todos with GET /todos/count

Builds on [001's design](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002's design](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid. The only changes are the ones listed here.

## Decisions

- **One `SELECT count(*)` in the repository.** `repository.count_todos(conn) -> int` runs `SELECT count(*) FROM todos` and returns the integer. The router never loads rows to count them, which is the point of the feature (AC-900.1). There is no filter, so the statement has no parameters.
- **A GET-only static route `/todos/count` on the existing router.** It is registered as `@router.get("/count")` in `todos/router.py`, placed above the `/{todo_id}` routes. No `PATCH` or `DELETE` handler is added for `/count`. Starlette picks the first route whose path *and* method match (a path-only match is kept only as a 405 fallback), so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo`. There `parse_id("count")` returns `None` and they answer `404 todo_not_found` exactly as for any non-UUID id (AC-900.2). No GET `/{todo_id}` route exists, so `GET /todos/count` cannot be shadowed either way.
- **No ADR.** Every decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list gains `GET /todos/count`, link to spec 900 | changed |

Key signatures (types only):

```python
# todos/repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos


# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...  # JSONResponse({"count": n})
```

## Contract

### `GET /todos/count`

| Condition | Response | Criteria |
|---|---|---|
| database answers | `200`, `Content-Type: application/json`, body exactly `{"count": <int>}` where `<int>` is the number of rows in `todos` (a JSON integer, `>= 0`, never a string) | AC-900.1, AC-900.2 |
| database unreachable or slower than 2.5 s | `503 unavailable` with 001's error body (`{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`) | (001 behaviour of `Database.run`) |

- The body has the single key `count`; no other keys.
- Query parameters are ignored (no filtering, no paging; spec non-goals).
- Done and open todos are both counted.

### Methods other than GET on `/todos/count`

Unchanged from 001/002: `/todos/count` is just a non-UUID id for the `/{id}` routes.

| Request | Response | Criteria |
|---|---|---|
| `PATCH /todos/count` with a valid body (`{"done": true}`) | `404`, `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, no database access | AC-900.2 |
| `DELETE /todos/count` | `404`, same body as above, no database access | AC-900.2 |
| `PATCH /todos/count` with an invalid body | `422` per 002's rule order (body rules come before the id rule) | unchanged |

All other endpoints (`GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, probes) are unchanged (AC-900.2).

### Test harness

No new fixtures. The acceptance tests go in a new file (e.g. `tests/test_todos_count.py`) and reuse `tests/conftest.py` as it is: `client` starts every test on a fresh `todos` table, so "given no todos" needs no setup and "given three todos" is three `POST /todos`. `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are not modified.

## Data

No change. No migration, no index (count over the whole table; the todo list is small).
