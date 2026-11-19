---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*) on the todos table'
tasks:
  - id: t1
    title: Add count_todos query and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
    done: true
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Answer `GET /todos/count` with `200 {"count": n}` computed in Postgres, without changing any existing route, per the contract in `design.md`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (parameterless) and returning the integer; the fetched row is never `None` for an aggregate, but guard it like `create_todo` does for mypy.
- `router.py`: add `@router.get("/count")` handler that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Do not name the handler the same as the imported repository function in a way that shadows it (it is accessed as `repository.count_todos`, so a handler named `count_todos` is fine).
- Leave `patch_todo` and `delete_todo` untouched: `parse_id("count")` already yields `None`, so they answer `404 todo_not_found` (AC-900.2).
- No new error codes, config, metrics or schema.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing test suite stays green, and `devbox run quality` passes.
