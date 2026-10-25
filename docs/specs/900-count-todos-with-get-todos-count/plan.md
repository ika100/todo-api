---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a single SELECT count(*), without changing the id routes'
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

Design: [design.md](design.md). This is a single task: the query and the route are about ten lines in two files, and the route cannot be tested without the query.

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Add `GET /todos/count`, which answers `200 {"count": <int>}` with the number of stored todos. The count comes from one `count(*)` query. The existing endpoints, including `PATCH`/`DELETE /todos/count` returning `404 todo_not_found`, stay exactly as they are.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`. Run `SELECT count(*) FROM todos` (no parameters), fetch one row and return `int(row[0])`. Raise `RuntimeError` if no row comes back, the same way `create_todo` does.
- `router.py`: add `@router.get("/count")` as `async def count_todos(request: Request) -> JSONResponse`. Call `await request.app.state.db.run(repository.count_todos)` and return `JSONResponse({"count": n})`. `JSONResponse` sets `Content-Type: application/json`.
- Do not touch `patch_todo` or `delete_todo`. `parse_id("count")` already returns `None`, which produces the `todo_not_found` 404 that AC-900.2 requires.
- Keep the module docstrings accurate. Add no new error codes, config or dependencies.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run quality` is green.
