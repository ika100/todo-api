---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "Add GET /todos/count returning a count object via one SELECT count(*), without shadowing PATCH/DELETE /todos/{id}"
tasks:
  - id: t1
    title: "Add repository.count_todos and the GET /todos/count route"
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). No ADR, no migration, no gitops, configuration or dependency change.

Levels: t1. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them or the existing test files.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`; `PATCH` and `DELETE /todos/count` still answer `404 todo_not_found`; nothing else changes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` executing `SELECT count(*) FROM todos` (no parameters) and returning the single value as `int` (raise `RuntimeError` if no row, like `create_todo`). Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that runs `repository.count_todos` through `request.app.state.db.run` and returns `JSONResponse({"count": n})`.
- Do not touch `patch_todo` or `delete_todo`: `"count"` fails `parse_id` and already yields `404 todo_not_found`. Do not add a `GET /{todo_id}` route.
- `README.md`: add `` - `GET /todos/count` number of todos (`{"count": n}`) `` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
