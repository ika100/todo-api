---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count returns the number of todos from a SELECT count(*), without shadowing the id routes"
tasks:
  - id: t1
    title: Add count_todos query and GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

One task: the query and the route are a few lines each and the route imports the query, so splitting them would only serialize work. Contract: [design.md](design.md).

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** expose the number of todos at `GET /todos/count` as `{"count": n}`, computed in the database, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` through the existing id routes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos`; return the integer (never `None`: `count(*)` always yields one row; raise `RuntimeError` like `create_todo` if it does not).
- `router.py`: add `@router.get("/count")` handler `count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})` (status 200, `application/json`).
- Declare the new route before `patch_todo`/`delete_todo` so a future `GET /{todo_id}` cannot shadow it. Register it for `GET` only; do not touch `patch_todo`, `delete_todo` or `parse_id`: `PATCH`/`DELETE /todos/count` already reach them and get `todo_not_found` because `parse_id("count")` is `None`.
- No changes to `main.py`, errors, schema or config.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
