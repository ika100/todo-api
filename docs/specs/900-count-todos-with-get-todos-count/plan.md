---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: GET /todos/count returns the number of todos, computed with count(*) in Postgres
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

One task: the query and the route are a few lines each and the route imports the query, so splitting them would only serialize two tiny tasks. See [design.md](design.md) for the contract.

## t1 — Add count_todos query and GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py
**Covers:** AC-900.1, AC-900.2
**Goal:** a caller gets the number of todos from `GET /todos/count` as `{"count": n}` without the list being loaded, and the id routes `PATCH`/`DELETE /todos/{todo_id}` keep answering `404 todo_not_found` for the literal id `count`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (fetch one row, take column 0; raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add `@router.get("/count")` with an async handler `count_todos(request: Request) -> JSONResponse` that calls `await request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})` (status 200, `application/json`).
- Register only `GET` on `/count`; do not add PATCH/DELETE handlers for it. Starlette prefers a full method+path match, so `PATCH`/`DELETE /todos/count` still reach `/{todo_id}`, where `parse_id("count")` is `None` and the existing `_not_found()` answers.
- Do not touch the other handlers, `to_json`, or the error module.
- Add unit tests only if coverage needs them; the acceptance tests run against the real Postgres fixture.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing tests in `tests/` still pass, and `devbox run quality` is green.
