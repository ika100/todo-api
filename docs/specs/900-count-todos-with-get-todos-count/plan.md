---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*); PATCH/DELETE /todos/count stay 404 todo_not_found'
tasks:
  - id: t1
    title: Add repository.count_todos and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). There is no ADR, no gitops change, no migration and no configuration change. This is a single level with one task: the route imports the repository function, so splitting them would only serialize two tiny changes.

The testers write the acceptance tests before coding, in a new file that uses the existing `tests/conftest.py`. No task edits them. Existing test files are not changed.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`. `PATCH` and `DELETE /todos/count` keep answering `404 todo_not_found`. Every other endpoint behaves exactly as before.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`. It runs `SELECT count(*) FROM todos` and returns the integer. If `fetchone()` returns `None`, it raises `RuntimeError`, as `create_todo` does. Use no parameters and leave `SCHEMA_SQL` unchanged.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": n})` with `n = await request.app.state.db.run(repository.count_todos)`. Place it directly after `list_todos`, before the `/{todo_id}` routes.
- Do not touch `patch_todo`, `delete_todo`, `validation.py` or `errors.py`. The existing `parse_id` path already gives `404 todo_not_found` for `count`.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, all existing tests pass unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
