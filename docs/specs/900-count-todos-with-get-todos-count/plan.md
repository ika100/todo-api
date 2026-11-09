---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: Add GET /todos/count, answered by one SELECT count(*), without shadowing the PATCH/DELETE id routes
tasks:
  - id: t1
    title: Add repository.count_todos
    files: [src/todo_api/todos/repository.py]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
  - id: t2
    title: Add the GET /todos/count route and document it
    files: [src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: [t1]
---

# Plan — 900 Count the todos with GET /todos/count

Contract: [design.md](design.md). No ADR, no gitops change, no migration, no configuration change (non-goals).

Levels: t1 → t2. The acceptance tests are written by the testers in a new file before coding, with the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`.

## t1 — Add repository.count_todos

**Files:** src/todo_api/todos/repository.py
**Covers:** AC-900.1, AC-900.2
**Goal:** count the todos in the database without loading them.

**Implementation notes:**
- Add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (fetch one row; raise `RuntimeError` if none, like `create_todo`).
- No parameters, no string building (bandit clean). Do not change `SCHEMA_SQL` or the other functions.

**Done when:** `devbox run quality` passes and all existing tests pass. The AC-900 acceptance tests pass after t2.

## t2 — Add the GET /todos/count route and document it

**Files:** src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` as JSON; the PATCH and DELETE id routes keep answering `404 todo_not_found` for `count`.

**Implementation notes:**
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`.
- Do not change `patch_todo`, `delete_todo`, `list_todos` or `create_todo`; `parse_id("count")` already yields `None` → `404 todo_not_found`.
- `README.md`: add `` - `GET /todos/count` number of todos (`{"count": n}`) `` after the `GET /todos` line, and a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged spec 001 and 002 tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
