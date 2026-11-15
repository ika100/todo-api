---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*), without changing the id routes'
tasks:
- id: t1
  title: Add repository.count_todos and the GET /todos/count route
  files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). No ADR, no migration, no gitops or configuration change.

Levels: t1. One task, because the query and the route that makes its acceptance tests pass cannot pass alone. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them or `tests/test_todos_api.py`.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning an `int`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` (handler e.g. `count_todos_route`) that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Database failures go through the existing `DatabaseUnavailable` → `503` mapping.
- Do not touch `patch_todo`, `delete_todo` or `validation.py`: `parse_id("count")` already returns `None`, which yields the existing `404 todo_not_found`.
- `README.md`: add `- GET /todos/count` count todos (`{"count": n}`) to the endpoint list and a link to spec 900 next to the existing spec links.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
