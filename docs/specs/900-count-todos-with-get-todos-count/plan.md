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

# Plan — 900 Count the todos with GET /todos/count

Design: [design.md](design.md). There is one task, because the route and its query only make sense together and touch two small files.

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Add `GET /todos/count`, which answers `200 {"count": n}` with `n` counted in the database. `PATCH` and `DELETE` on `/todos/count` keep falling through to the id routes, which answer `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`. It runs `SELECT count(*) FROM todos` and returns the integer, raising `RuntimeError` if there is no row (same pattern as `create_todo`).
- `router.py`: add `@router.get("/count")` with handler `count_todos(request: Request) -> JSONResponse`. It calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`.
- Declare the route before `@router.patch("/{todo_id}")`. Register it for GET only; do not add PATCH or DELETE handlers for `/count`.
- Do not change `parse_id`, `_not_found` or the existing handlers. `parse_id("count")` already returns `None`, so the id routes already give `404 todo_not_found`.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run ci` is green.
