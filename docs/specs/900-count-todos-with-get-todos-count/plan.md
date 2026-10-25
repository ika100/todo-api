---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*), without shadowing PATCH/DELETE /todos/{id}'
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

Contract and routing decision: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. One task: the repository function and the route are a few lines each and the route imports the function, so splitting them would only serialize two tiny tasks. The acceptance tests for this spec are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them or any existing test file. There is no migration, no gitops change, and `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `n` counted by the database, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every other endpoint is unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters); return the integer from `fetchone()`, raising `RuntimeError` if no row comes back, like `create_todo`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`.
- Register only `GET` for `/count`. Do not add PATCH/DELETE handlers for it and do not add a `GET /{todo_id}` route; the existing `/{todo_id}` PATCH/DELETE routes must keep receiving `todo_id="count"` (design, Decisions).
- Leave `list_todos`, `create_todo`, `patch_todo`, `delete_todo`, `to_json` and error handling untouched.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and add a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`, unit tests) pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
