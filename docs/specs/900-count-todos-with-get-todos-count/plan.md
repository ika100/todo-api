---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*), without touching the id routes'
tasks:
- id: t1
  title: Add repository.count_todos and the GET /todos/count route
  files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
  done: true
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). There is no ADR and no gitops task: every decision is local to this feature, and the spec excludes gitops, configuration and schema changes.

Levels: t1. One task, because the query and the route that makes its acceptance tests pass cannot pass separately. The acceptance tests are written by the testers before coding with the existing `tests/conftest.py` harness; no task edits them, nor `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`; the id routes and every existing endpoint behave as before.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running the bound-parameter-free `SELECT count(*) FROM todos`; return `0` if no row comes back. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it next to `list_todos`, above the `/{todo_id}` routes.
- Do not change `patch_todo`, `delete_todo`, `parse_id` or `errors.py`: `PATCH`/`DELETE /todos/count` already answer `404 todo_not_found` because `"count"` is not a UUID.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and every existing test pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
