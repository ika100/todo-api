---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count returns {\"count\": n} from a SELECT count(*), without shadowing the id routes"
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
**Goal:** Serve `GET /todos/count` with `200 {"count": n}` computed in the database, leaving `PATCH`/`DELETE /todos/count` and every existing endpoint unchanged (contract in design.md).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`.
- Register only `GET` for `/count`; do not add `PATCH`/`DELETE` handlers for it, so those still reach `/{todo_id}` and answer `todo_not_found` 404 via `parse_id`.
- Do not change `list_todos`, `create_todo`, `patch_todo`, `delete_todo` or the error handlers.
- A unit-level check of `count_todos` is optional; the acceptance tests exercise it end to end.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
