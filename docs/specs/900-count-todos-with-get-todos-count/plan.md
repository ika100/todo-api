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

Design and contract: [design.md](design.md). No ADR: every decision is local to this feature.

Levels: t1. One task, because the repository function and the route are a few lines each and splitting them would only add a dependency. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, nor `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. No migration, no config, no gitops change; `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every existing endpoint is unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the value as `int`. Leave `SCHEMA_SQL` and the other queries unchanged.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Declare it next to `list_todos`, before the `/{todo_id}` routes.
- Do not change `patch_todo`, `delete_todo`, `parse_id` or the error handlers: the `/{todo_id}` routes already answer `404 todo_not_found` for `count` (design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 next to the spec 002 link.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
