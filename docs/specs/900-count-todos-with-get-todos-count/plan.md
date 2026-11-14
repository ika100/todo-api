---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*) without shadowing the id routes'
tasks:
  - id: t1
    title: Add count_todos query and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
    done: true
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Callers get the number of todos from `GET /todos/count` as `{"count": n}` without the list being read, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` through the existing id handlers (see design.md, Contract).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (fetchone; raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`.
- Add only a `GET` route; do not add PATCH/DELETE handlers for `/count` and do not change the existing handlers: method-based matching already sends those to `/{todo_id}`, where `parse_id` rejects `"count"` with `todo_not_found`.
- No new module, no config, no schema change.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
