---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count returns {\"count\": n} from a SELECT count(*) query"
tasks:
  - id: t1
    title: Add count query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Return the number of todos from `GET /todos/count` as `{"count": n}`, per the contract in design.md, without changing any existing route.

**Implementation notes:**
- `repository.count_todos(conn: AsyncConnection) -> int`: `SELECT count(*) FROM todos`, return the integer (0 when empty).
- `router.py`: add `@router.get("/count")` handler `get_todo_count`, running `repository.count_todos` through `request.app.state.db.run(...)` and returning `JSONResponse({"count": n})`.
- Do not touch the `PATCH`/`DELETE /{todo_id}` handlers: they already answer `404 todo_not_found` for `count` because `parse_id` rejects it.
- No schema, config, or gitops change.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
