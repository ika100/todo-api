---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n}, counted in the database'
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
**Goal:** Expose the number of todos at `GET /todos/count` as `{"count": n}`. The count is computed with one `count(*)` query and the existing id routes keep their behaviour. The contract is in `design.md`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns the value as `int`.
- `router.py`: add `@router.get("/count")` and declare it before the `/{todo_id}` routes. It returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`.
- Leave the PATCH and DELETE handlers unchanged. They already answer `todo_not_found` for `count`, because `parse_id` rejects it.
- Add unit tests under `tests/` for `count_todos` if coverage needs them. Do not edit the acceptance tests.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/test_todos_api.py` still pass, and `devbox run ci` is green.
