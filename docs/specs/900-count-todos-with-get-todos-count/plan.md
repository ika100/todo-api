---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} computed with SELECT count(*), without shadowing the id routes'
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
**Goal:** a caller gets the number of todos from `GET /todos/count` as `{"count": n}`, computed in the database, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` through the existing id routes. Contract in `design.md`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add a `@router.get("/count")` handler that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})` (status 200, `application/json`).
- Add no `PATCH` or `DELETE` handler for `/count`; the existing `/{todo_id}` handlers already answer `404 todo_not_found` for `count` because `parse_id` rejects it.
- Do not change the other handlers. The acceptance tests exercise both new functions; no other test file is edited.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests still pass, and `devbox run ci` is green.
