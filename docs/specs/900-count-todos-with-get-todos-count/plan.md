---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} computed with SELECT count(*)'
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

One task: the query and the route are a few lines each and the route is untestable without the query, so splitting would only serialize two tiny tasks. Contract: [design.md](design.md).

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, where `n` is counted in the database, without changing any existing route.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos`; return the integer (raise `RuntimeError` if no row comes back, like `create_todo`).
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that runs `repository.count_todos` through `request.app.state.db.run(...)` and returns `JSONResponse({"count": n})`. Follow the existing handler style (no response_model).
- Do not touch the `PATCH /{todo_id}` and `DELETE /{todo_id}` handlers: they already answer `404 todo_not_found` for `count` because `parse_id("count")` is `None`, and Starlette prefers their full match over the GET-only `/count` route.
- Database unavailability is handled by the existing `DatabaseUnavailable` handler (503); no new error code.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing suite (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) still passes, and `devbox run quality` is green.
