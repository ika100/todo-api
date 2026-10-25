---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: Add GET /todos/count returning the number of todos via one SELECT count(*), without shadowing the id routes
tasks:
- id: t1
  title: Add repository.count_todos
  files: [src/todo_api/todos/repository.py]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Add the GET /todos/count route and document it
  files: [src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: false
  depends_on: [t1]
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). No ADR, no migration, no gitops change; `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

Levels: t1 → t2. The acceptance tests are written by the testers in a new test file before coding, using the existing `tests/conftest.py` harness. No task edits them, and no task touches `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`.

## t1 — Add repository.count_todos

**Files:** src/todo_api/todos/repository.py
**Covers:** AC-900.1, AC-900.2
**Goal:** one query that returns how many todos exist.

**Implementation notes:**
- Add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer from the single row.
- If `fetchone()` returns `None`, raise `RuntimeError` (same style as `create_todo`); it cannot happen for `count(*)`.
- No parameters, no string formatting (bandit clean). Do not change `SCHEMA_SQL` or the other functions.

**Done when:** `devbox run quality` passes and all existing tests pass. The AC-900 acceptance tests pass after t2.

## t2 — Add the GET /todos/count route and document it

**Files:** src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`; `PATCH` and `DELETE /todos/count` keep answering `404 todo_not_found`.

**Implementation notes:**
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Database errors propagate unchanged (the existing handlers map them to `503 unavailable`).
- Register only GET on `/count`. Do not add PATCH/DELETE handlers or an `api_route` with other methods for it, and do not change `patch_todo` or `delete_todo`: they already return `404 todo_not_found` for the non-UUID id `count`.
- `README.md`: add ``- `GET /todos/count` number of todos (`{"count": n}`)`` after the `GET /todos` line, and add a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged spec 001 and 002 test files pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
