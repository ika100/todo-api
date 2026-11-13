---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*) without shadowing the id routes'
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Callers get the number of todos from `GET /todos/count` as `{"count": n}` with one `SELECT count(*)`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` through the existing id handlers. Contract: `design.md`.

**Implementation notes:**
- `repository.py`: `async def count_todos(conn: AsyncConnection) -> int` runs `SELECT count(*) FROM todos` and returns the integer (raise `RuntimeError` if no row comes back, like `create_todo`).
- `router.py`: `@router.get("/count")` handler `count_todos(request: Request) -> JSONResponse` returns `JSONResponse({"count": n})` where `n = await request.app.state.db.run(repository.count_todos)`.
- Add only a GET route for `/count`; do not touch `patch_todo` / `delete_todo`. `parse_id("count")` already returns `None`, which produces the `todo_not_found` 404.
- Keep `mypy` strict-clean (return `int`, not `Any`).

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run quality` is green.
