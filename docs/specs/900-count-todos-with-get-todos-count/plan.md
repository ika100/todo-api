---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count returns the number of todos from a SELECT count(*), without shadowing the id routes"
tasks:
  - id: t1
    title: "Add count_todos query and GET /todos/count route"
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Add `GET /todos/count`, which answers `200 {"count": <int>}` with the number of rows in `todos`. `PATCH /todos/count` and `DELETE /todos/count` still answer `404 todo_not_found`, and no existing endpoint changes. The contract is in [design.md](design.md).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`. It runs `SELECT count(*) FROM todos`, reads the single row and returns it as `int`. Follow the style of the existing queries (parameterized and typed, no ORM).
- `router.py`: add `@router.get("/count")` with `async def count_todos(request: Request) -> JSONResponse`. It calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Declare it directly after `list_todos`, before the `/{todo_id}` routes.
- Do not change `patch_todo` or `delete_todo`. `parse_id("count")` already returns `None`, so both handlers raise `todo_not_found`. Confirm this with the acceptance test, and add no special case.
- No schema, config, env or gitops change.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, the existing tests in `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run quality` is green.
