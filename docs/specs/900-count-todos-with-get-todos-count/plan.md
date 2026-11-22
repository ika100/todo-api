---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns the number of todos as {"count": n}, computed with SELECT count(*)'
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Expose `GET /todos/count` answering `200 {"count": <int>}` with `application/json`, counted in the database, without changing any existing route (contract in design.md).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the value as `int`.
- `router.py`: add `@router.get("/count")` handler declared directly after `list_todos`, calling `request.app.state.db.run(repository.count_todos)` and returning `JSONResponse({"count": n})`.
- Do not add PATCH/DELETE handlers for `/count`; the existing id routes already answer `404 todo_not_found` because `parse_id("count")` is `None`.
- Database errors flow through `db.run` and the existing `DatabaseUnavailable` handler (503); no new error codes.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
