---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*) and leaves the id routes untouched'
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
**Goal:** Add an endpoint that returns how many todos exist without loading the list. It follows the contract in design.md and leaves every existing route as it is.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`. It runs `SELECT count(*) FROM todos` and returns the single value as an `int`. It raises `RuntimeError` if no row comes back, like `create_todo` does.
- `router.py`: add `@router.get("/count")` that returns `JSONResponse({"count": n})`, where `n = await request.app.state.db.run(repository.count_todos)`. Going through `db.run` keeps the existing deadline and 503 handling.
- Do not change `patch_todo` or `delete_todo`. `parse_id("count")` already returns `None`, which gives the `todo_not_found` 404 that AC-900.2 asserts.
- Do not add a `GET /{todo_id}` route or change any other handler (non-goal).

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing test suite passes unchanged, and `devbox run quality` is green.
