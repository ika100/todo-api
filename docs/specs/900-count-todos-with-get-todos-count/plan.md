---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning the number of todos from one SELECT count(*), without shadowing PATCH or DELETE /todos/{id}'
tasks:
- id: t1
  title: Add repository.count_todos and the GET /todos/count route
  files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Contract: [design.md](design.md). No ADR, no migration, no gitops change, no new configuration. `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

Levels: t1. One task: the repository function and the route are a few lines each, and splitting them would only add a real dependency (the route imports the function) without any parallelism. The acceptance tests for AC-900.1 and AC-900.2 are written by the testers before coding with the existing `tests/conftest.py` harness; no task edits them, and no task touches the existing test files.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, computed by the database, while `PATCH` and `DELETE /todos/count` keep answering `404 todo_not_found` and every existing endpoint is unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (fetch the single row; raise `RuntimeError` if no row comes back, like `create_todo`). Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it directly after `list_todos`, before the `/{todo_id}` routes.
- Do not touch `patch_todo`, `delete_todo`, `parse_id` or the error handlers: `PATCH`/`DELETE /todos/count` already resolve to the `/{todo_id}` routes and answer `404 todo_not_found` (design, Decisions).
- Database unavailability flows through `Database.run` and the existing `503 unavailable` handler; add no new error handling.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 next to the existing spec links if the README lists them.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, all existing tests (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`, unit tests) pass unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
