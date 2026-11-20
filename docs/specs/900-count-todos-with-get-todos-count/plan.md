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
**Goal:** Callers get the number of todos from `GET /todos/count` as `200 {"count": n}` (contract in design.md), computed in the database, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every existing endpoint stays as it is.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` returning `JSONResponse({"count": n})` where `n = await request.app.state.db.run(repository.count_todos)`; name the handler so it does not shadow the imported module function (e.g. `count_todos_route`).
- Do not touch `patch_todo`/`delete_todo`: the static GET route does not capture other methods, so `parse_id("count")` keeps producing `404 todo_not_found`.
- Database unreachability is handled by the existing `DatabaseUnavailable` handler; add nothing.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing suite stays green, and `devbox run quality` passes.
