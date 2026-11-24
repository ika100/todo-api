---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count, which returns {"count": n} from one SELECT count(*), with no change to the id routes'
tasks:
- id: t1
  title: Add repository.count_todos and the GET /todos/count route
  files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Contract: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. The task is not split: the repository function is useful only together with the route, and a split would serialize two very small tasks for no benefit. The testers write the acceptance tests in a new test file with the existing `tests/conftest.py` harness, and no task edits that file. There is no migration and no gitops change, and `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` as `application/json`. PATCH and DELETE on `/todos/count` keep answering `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`, which runs `SELECT count(*) FROM todos` and returns the integer. If `fetchone()` returns no row, raise `RuntimeError` the way `create_todo` does. Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count")` as `count_todos(request) -> JSONResponse`, which returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Database errors go through the existing `db.run` path and become `503 unavailable`.
- Do not change `patch_todo`, `delete_todo`, `list_todos` or `create_todo`. `"count"` already fails `parse_id` and answers `404 todo_not_found`.
- `README.md`: add `- \`GET /todos/count\` count todos (\`{"count": n}\`)` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged spec 001 and 002 tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
