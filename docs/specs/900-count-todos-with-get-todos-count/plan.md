---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from a SELECT count(*), without shadowing the id routes'
tasks:
- id: t1
  title: Add repository.count_todos and the GET /todos/count route
  files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Contract and routing decision: [design.md](design.md). No ADR, no gitops change, no migration, no new environment variable.

Levels: t1. One task: the repository function and the route are a few lines each and the route is untestable without the query, so splitting them would only serialize work. The acceptance tests are written by the testers before coding with the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`; `PATCH`/`DELETE /todos/count` still answer `404 todo_not_found`; every other endpoint is unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (`fetchone()`; raise `RuntimeError` if no row, like `create_todo`). Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count") async def count_todos(request)` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Register it directly after `list_todos`, above the `/{todo_id}` routes.
- Do not touch `patch_todo`, `delete_todo`, `parse_id` or the error handlers: `"count"` is not a UUID, so the id routes already answer `404 todo_not_found` (design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
