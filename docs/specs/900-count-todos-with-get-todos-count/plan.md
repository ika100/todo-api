---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from one SELECT count(*), without shadowing the id routes'
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
**Goal:** Expose the number of todos at `GET /todos/count` as `{"count": n}` per the contract in `design.md`, reading it with one `SELECT count(*)` and leaving every existing endpoint, including `PATCH`/`DELETE /todos/{id}` for the id `count`, unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (raise `RuntimeError` if no row, like `create_todo`).
- `router.py`: add `@router.get("/count")` handler `count_todos(request)` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`; declare it above the `/{todo_id}` routes.
- Register only `GET` on `/count`; do not add a `PATCH`/`DELETE` handler for it, so those keep falling through to `/{todo_id}` and answer `todo_not_found` 404.
- The acceptance tests exercise both functions end to end; the repo has no repository unit tests, so none are added.

**Done when:** the acceptance tests for AC-900.1 and AC-900.2 pass, the existing test suite passes unchanged, and `devbox run quality` is green.
