---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*), without shadowing the id routes'
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Callers learn how many todos exist without downloading the list. The repository gains a count query and the `/todos` router gains `GET /count`, answering the contract in `design.md`.

**Implementation notes:**
- `repository.py`: `async def count_todos(conn: AsyncConnection) -> int` runs `SELECT count(*) FROM todos` and returns the integer (raise `RuntimeError` if no row comes back, like `create_todo`).
- `router.py`: `@router.get("/count")` handler that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`.
- Do not change `patch_todo` or `delete_todo`: they already answer `404 todo_not_found` for `count`, because `parse_id("count")` is `None` (AC-900.2).
- Keep the database access inside `db.run` so an unreachable database answers the existing `503 unavailable`.
- Do not edit the acceptance test files.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, the existing test suite still passes, and `devbox run quality` is green.
