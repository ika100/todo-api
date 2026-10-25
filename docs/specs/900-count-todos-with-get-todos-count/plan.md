---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from one SELECT count(*), without shadowing the id routes'
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

The contract and the route-order decision are in [design.md](design.md). There is no ADR, no migration and no gitops change. `pyproject.toml`, the `Dockerfile`, CI and `docs/env-vars.md` stay as they are.

Levels: t1. This is one task: the route needs the repository function, and splitting it would only serialize two very small edits. The testers write the AC-900 acceptance tests in a new test file before coding, using the existing `tests/conftest.py` harness. No task edits that file or `tests/test_todos_api.py` / `tests/test_todos_title_patch.py`.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`. `PATCH /todos/count` and `DELETE /todos/count` keep answering `404 todo_not_found`, and every existing endpoint behaves as before.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`, which runs `SELECT count(*) FROM todos` and returns the value as a Python `int`. If `fetchone()` returns `None`, raise `RuntimeError` (same style as `create_todo`). Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse`. It calls `await request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Declare it directly after `list_todos`/`create_todo`, before the `/{todo_id}` routes.
- Do not add a `GET /{todo_id}` route. Do not touch `patch_todo`, `delete_todo`, `parse_id` or the error handlers. `count` already fails `parse_id`, so it gives the existing 404 (AC-900.2).
- `README.md`: add the line `` - `GET /todos/count` number of todos (`{"count": n}`) `` after `GET /todos`. Add a link to spec 900 next to the existing spec links if there are any.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, and so do all existing tests (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`, unit tests), unchanged, with `devbox run test`. `devbox run quality` and `devbox run security` also pass.
