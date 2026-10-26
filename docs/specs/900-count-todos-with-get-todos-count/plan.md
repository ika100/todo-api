---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count returns the number of todos from a SQL count, without shadowing the id routes"
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

One task: the query and the route are a few lines each, and the route imports the query, so splitting them would only serialize two tiny tasks. Contract: [design.md](design.md).

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** a caller gets the number of todos from `GET /todos/count` as `{"count": n}`, while `PATCH`/`DELETE /todos/count` still answer `404 todo_not_found` and the other endpoints are unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos`; return the value as a Python `int` (raise `RuntimeError` if no row comes back, matching `create_todo`).
- `router.py`: add `@router.get("/count")` `count_todos(request: Request) -> JSONResponse`, calling `request.app.state.db.run(repository.count_todos)` and returning `JSONResponse({"count": n})` (which sets `Content-Type: application/json`).
- Declare the route before the `/{todo_id}` routes. Do not change `patch_todo`, `delete_todo` or `parse_id`: `"count"` is not a UUID, so they keep answering `404 todo_not_found`.
- Database failures go through the existing `DatabaseUnavailable` → `503` mapping; no new error handling.
- No schema, config or gitops change.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run quality` is green.
