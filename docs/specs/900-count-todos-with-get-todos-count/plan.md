---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns the number of todos as {"count": n}'
tasks:
  - id: t1
    title: Add GET /todos/count backed by a count query
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add GET /todos/count backed by a count query

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** Callers get the number of todos from `GET /todos/count` as `{"count": n}` without downloading the list, while `PATCH`/`DELETE /todos/count` keep answering the existing `404 todo_not_found` (see design.md, Contract).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer.
- `router.py`: add `@router.get("/count")` handler `count_todos(request) -> JSONResponse` that runs `repository.count_todos` via `request.app.state.db.run` and returns `JSONResponse({"count": n})`.
- Add only the GET route; do not touch `patch_todo`/`delete_todo` — `parse_id("count")` already returns `None`, which yields `todo_not_found`.
- `README.md`: add `GET /todos/count` to the endpoint list.
- Unit/integration tests beyond the acceptance tests are optional; keep coverage at the repo's gate.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests still pass, and `devbox run ci` is green.
