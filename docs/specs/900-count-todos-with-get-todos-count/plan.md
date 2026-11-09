---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*), without shadowing the PATCH/DELETE id routes'
tasks:
  - id: t1
    title: Add repository.count_todos and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Contract: [design.md](design.md). No ADR, no migration, no gitops change; `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change. The acceptance tests are written by the testers before coding with the existing `tests/conftest.py` harness; no task edits them or `tests/test_todos_api.py` / `tests/test_todos_title_patch.py`.

One task: the repository function and the route are a few lines each and the route is untestable without the function, so splitting them would only serialize the work.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` as `application/json`; `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found`; nothing else changes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (fetch one row; raise `RuntimeError` if no row, like `create_todo`). Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count")` handler `count_todos(request)` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it next to `list_todos`.
- Do not touch `patch_todo`, `delete_todo` or `validation.py`: `parse_id("count")` already returns `None`, which yields `404 todo_not_found` (design, "Neighbouring routes").
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
