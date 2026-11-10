---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from a SELECT count(*), without changing the id routes'
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

Levels: t1. One task, because the route imports the only other change (the repository function) and the whole feature is a single focused pass. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them. No task touches `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. There is no migration, and `pyproject.toml`, `Dockerfile`, CI, `docs/env-vars.md` and the gitops repo do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, counted in the database, while `PATCH /todos/count` and `DELETE /todos/count` keep answering `404 todo_not_found` through the unchanged id routes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the first column as `int`; raise `RuntimeError` if no row comes back, like `create_todo`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that calls `await request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it directly after `list_todos`, before the `/{todo_id}` routes.
- Do not change `patch_todo`, `delete_todo`, `parse_id` or the error handlers: `"count"` is not a UUID, so the existing code already answers `404 todo_not_found` (design, "Unchanged routes").
- No query parameters, no filtering, no new metric or log line.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
