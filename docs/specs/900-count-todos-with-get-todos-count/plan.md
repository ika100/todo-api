---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from a SELECT count(*), without shadowing the id routes'
tasks:
  - id: t1
    title: Add count_todos query and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

## t1 — Add count_todos query and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** a caller gets the number of todos from `GET /todos/count` as `{"count": n}`, computed in the database, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and the other endpoints stay unchanged (contract in design.md).

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` executing `SELECT count(*) FROM todos`; return the integer (raise `RuntimeError` if no row, as `create_todo` does).
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": count})`. Going through `db.run` keeps the existing 503 behaviour.
- Do not touch the `/{todo_id}` handlers: with no `GET /{todo_id}` route, `PATCH`/`DELETE /todos/count` still reach them and `parse_id("count")` yields the 404.
- One commit: one task, since the route without the query (or vice versa) cannot pass its checks alone.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run ci` is green.
