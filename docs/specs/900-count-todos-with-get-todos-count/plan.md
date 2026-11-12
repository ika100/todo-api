---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*) without shadowing the id routes'
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
**Goal:** Add `GET /todos/count`. It answers `200 {"count": n}` with n taken from `SELECT count(*) FROM todos`. `PATCH` and `DELETE /todos/count` must keep reaching the id handlers and answer `404 todo_not_found`. The contract is in design.md.

**Implementation notes:**
- `repository.count_todos(conn: AsyncConnection) -> int`: a parameterless `SELECT count(*) FROM todos` that returns an `int`. Follow the style of `delete_todo` (use `conn.execute`).
- `router.py`: add `@router.get("/count")` with handler `count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": n})`, using `request.app.state.db.run(repository.count_todos)`. Put it above the `/{todo_id}` routes.
- Register only GET on `/count`. Do not touch `patch_todo` or `delete_todo`. They already turn the non-UUID `count` into `todo_not_found`.
- The acceptance tests are already in place and coders do not edit them.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
