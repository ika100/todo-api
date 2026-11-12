---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'GET /todos/count returns {"count": n} from one SELECT count(*), without shadowing PATCH/DELETE /todos/{id}'
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

The contract is in [design.md](design.md). There is no ADR and no gitops change, and there is no migration. `pyproject.toml`, the `Dockerfile`, CI and `docs/env-vars.md` do not change. The testers write the AC-900 acceptance tests in a new file before coding, using the existing `tests/conftest.py` harness. No task edits that file or `tests/test_todos_api.py`.

This is a single task: the query and the route that makes it observable only pass their checks together.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`. `PATCH` and `DELETE /todos/count` keep answering `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns it as an `int` (0 for an empty table). Keep `SCHEMA_SQL` unchanged and use no string-built SQL.
- `router.py`: add `@router.get("/count")`, which returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Name the handler `count_todos_route` (or similar) so that it does not shadow the imported module function in readers' minds. Register it as `GET` only.
- Do not add a `GET /{todo_id}` route and do not special-case `"count"` in `patch_todo` or `delete_todo`. The existing `parse_id` → `404` path already produces AC-900.2.
- `README.md`: add `` - `GET /todos/count` number of todos (`{"count": n}`) `` after the `GET /todos` line, and link spec 900 next to the spec 001/002 links if such links exist.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
