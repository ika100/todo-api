---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 0fe512a9e20b
summary: "GET /todos/count returns the number of todos, computed with SELECT count(*)"
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Contract: [design.md](design.md#contract).

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Expose the number of todos as `GET /todos/count` → `200 {"count": <int>}` with `Content-Type: application/json`, counted in the database without loading the rows.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos`; return the value as a Python `int` (raise `RuntimeError` if no row comes back, like `create_todo`).
- `router.py`: add `@router.get("/count")` handler `count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`.
- Declare the new route directly after `list_todos`, before the `/{todo_id}` routes, so the literal path is matched first should a `GET /todos/{id}` ever be added.
- Do not touch the other handlers, `main.py`, or the schema.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run quality` is green.
