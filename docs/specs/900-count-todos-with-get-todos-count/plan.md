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

Design and contract: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. One task, because the route cannot pass its acceptance tests without the query and the query alone has no caller. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. There is no migration, and `pyproject.toml`, `Dockerfile`, CI, `docs/env-vars.md` and the gitops repo do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and no other endpoint changes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters, bandit clean) and returning `int(row[0])`; a missing row raises `RuntimeError`, like `create_todo`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` handler `count_todos(request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Declare it above `patch_todo`. Do not touch `patch_todo`, `delete_todo` or `parse_id`: `"count"` is not a UUID, so they already answer `404 todo_not_found`.
- No new error handling: `DatabaseUnavailable` maps to `503 unavailable` through the existing handler.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 next to the spec 002 link.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, all existing tests pass unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
