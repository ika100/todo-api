# Design — 900 Count the todos with GET /todos/count

This builds on the designs of [001](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002](../002-change-a-todo-s-title-through-patch/design.md). Everything in them still holds. This spec adds one read-only route and changes nothing else.

## Decisions

- **Count in SQL with `SELECT count(*) FROM todos`.** Fetching the rows and counting them in Python is what the spec wants callers to stop doing. One statement through `request.app.state.db.run`, like the other queries, so the 2.5 s deadline and the `503 unavailable` mapping apply unchanged.
- **Add only a `GET` route at `/todos/count`.** No `GET /todos/{id}` exists, so the new route shadows nothing. `PATCH /todos/count` and `DELETE /todos/count` still reach the existing `/{todo_id}` handlers. Starlette prefers a full (path and method) match over a path-only match, so the GET route never turns them into `405`. `parse_id("count")` returns `None`, so both answer `404 todo_not_found` exactly as for any non-UUID id (AC-900.2). Declare the route before the `/{todo_id}` routes in `router.py` anyway, so a later `GET /todos/{id}` cannot shadow it.
- **No ADR.** The decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | the endpoint list includes `GET /todos/count` | changed |

```python
# todos/repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos


# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...
```

## Contract

### `GET /todos/count`

- `200`, `Content-Type: application/json`, body is exactly `{"count": <int>}`: a JSON integer >= 0 with no other keys. It is the number of rows in `todos`. Filters and paging do not exist, and query parameters are ignored (AC-900.1, AC-900.2).
- The database is unreachable or slower than 2.5 s: `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`. This is the same as `GET /todos`.
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body (for example `{"done": true}`) returns `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). The existing PATCH rule order is unchanged. An invalid body still gets its `422` first, as for any id.
  - `DELETE /todos/count` returns the same `404 todo_not_found` (AC-900.2).
  - `POST /todos/count` returns `405 method_not_allowed`. That is the existing generic handling, and no criterion depends on it.
- `GET`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` and the probes stay unchanged.

### Test harness

There are no new fixtures. The acceptance tests go in a new file (for example `tests/test_todos_count.py`) and use the existing `client` fixture from `tests/conftest.py`. They create three todos with `POST /todos` for AC-900.1, and they start from an empty table for AC-900.2. The existing test files are not modified.

## Data

Nothing changes. There is no migration and no index. `count(*)` on `todos` is a sequential or index-only scan, which is fine at this service's scale.

## Risks

- None worth tracking. Under concurrent writes, the count is a snapshot as of the statement (READ COMMITTED). That is acceptable for a number the caller cannot act on atomically anyway.
