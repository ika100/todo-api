---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} computed with SELECT count(*)'
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
    done: true
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Callers get the number of todos from `GET /todos/count` as `{"count": n}` without downloading the list, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` (contract in design.md).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running the parameterless `SELECT count(*) FROM todos`; return a plain `int`.
- `router.py`: add `@router.get("/count")` handler that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Give the handler a name that does not clash with the imported module function (e.g. `count_todos_route`).
- Do not touch the `PATCH`/`DELETE` `/{todo_id}` handlers; `parse_id("count")` already yields `None`, giving the required `404`.
- Keep the one query in one module; no new config, schema or dependency.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests still pass, and `devbox run quality` is clean.
