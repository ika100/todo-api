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

Design and contract: [design.md](design.md). No ADR, no migration, no gitops or configuration change (non-goals).

Levels: t1. One task, because the query and the route that makes its acceptance tests pass cannot pass separately. The acceptance tests are written by the testers before coding with the existing `tests/conftest.py` harness; no task edits them or `tests/test_todos_api.py`.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`; `PATCH`/`DELETE /todos/count` still answer `404 todo_not_found`; every other endpoint behaves as before.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (`fetchone()[0]`; a missing row raises `RuntimeError`, like `create_todo`). Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` returning `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Place it after `list_todos` and before `patch_todo`. Register GET only; add no handler for other methods on `/count`.
- Do not change `patch_todo`, `delete_todo` or `parse_id`: they already turn `count` into `404 todo_not_found`.
- `README.md`: add `- \`GET /todos/count\` count todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 next to the existing spec links.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged spec 001 and 002 tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
