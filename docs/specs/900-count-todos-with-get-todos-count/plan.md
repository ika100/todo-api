---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns the number of todos as {"count": n}'
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
**Goal:** Serve `GET /todos/count` with `200 {"count": n}` computed in the database, without changing any existing endpoint (contract in design.md).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add `@router.get("/count")` handler `count_todos(request: Request) -> JSONResponse` that runs `repository.count_todos` via `request.app.state.db.run` and returns `JSONResponse({"count": n})`.
- Do not touch the `PATCH`/`DELETE /{todo_id}` handlers: `parse_id("count")` already yields `None` -> `404 todo_not_found`.
- Keep the route free of query parameters; no filtering (non-goal).

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is clean.
