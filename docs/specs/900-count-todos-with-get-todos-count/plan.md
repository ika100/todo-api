---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*), without shadowing the id routes'
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

The design and the binding contract are in [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. There is one task, because the repository function and the route that makes its acceptance tests pass are one change. The testers write the acceptance tests in a new file before coding, with the existing `tests/conftest.py` harness. No task edits that file or `tests/test_todos_api.py`. Nothing else changes: there is no migration, no new config or env var, and no gitops, `pyproject.toml`, `Dockerfile` or CI change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}`, and `n` is counted in the database. `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`, which runs `SELECT count(*) FROM todos` and returns it as `int`. It takes no parameters and leaves `SCHEMA_SQL` unchanged.
- `router.py`: add `@router.get("/count")` with `async def count_todos(request: Request) -> JSONResponse`. It calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it after `create_todo` and before `patch_todo`.
- Do not add PATCH/DELETE handlers for `/count`, and do not touch `patch_todo`/`delete_todo` or `parse_id`. The 404 for `/todos/count` comes from the existing id handlers (see design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line. Add a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
