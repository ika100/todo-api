---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count returns the todo count from a SELECT count(*) on the todos table"
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
    done: true
---

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Add a `count_todos` repository function and a `GET /todos/count` handler on the existing `/todos` router. The handler returns `200 {"count": n}` as `application/json`. PATCH and DELETE on `/todos/count` keep returning the existing `404 todo_not_found`. See the contract in design.md.

**Implementation notes:**
- `repository.py`: `async def count_todos(conn: AsyncConnection) -> int` runs `SELECT count(*) FROM todos`, reads the single row and returns `int(row[0])`. It raises `RuntimeError` if no row comes back, mirroring `create_todo`.
- `router.py`: `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`.
- Leave the `patch_todo` and `delete_todo` handlers unchanged. `parse_id("count")` already returns `None`, which yields `todo_not_found`.
- Database errors go through `db.run` and the global handler (503 `unavailable`) like the other endpoints. Add no extra handling.
- Do not change `GET /todos`, the schema or any configuration (non-goals).

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` still pass, and `devbox run quality` is green.
