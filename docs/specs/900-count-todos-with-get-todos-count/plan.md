---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*) and leaves the id routes untouched'
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

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** Add an endpoint that answers `GET /todos/count` with `200 {"count": n}`. The database computes `n`. `PATCH` and `DELETE` on `/todos/count` keep returning the existing `404 todo_not_found`, as specified in design.md.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns the integer. If no row comes back, raise `RuntimeError`, following `create_todo`.
- `router.py`: add `@router.get("/count")` with `async def count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`.
- Register only `GET`. Do not add a special case for `count` to the patch or delete handlers: they already return `todo_not_found` because `parse_id("count")` is `None`.
- Do not touch the existing handlers, `to_json`, validation, errors or the schema.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, all existing tests still pass, and `devbox run quality` is green.
