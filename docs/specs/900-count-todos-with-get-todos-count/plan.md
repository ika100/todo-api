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
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). There is no ADR and no gitops task, and there is no migration. `pyproject.toml`, the `Dockerfile`, CI and `docs/env-vars.md` do not change. The testers write the AC-900 acceptance tests in a new file before coding, using the existing `tests/conftest.py` harness. No task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`.

Levels: t1. This is one task, because the query and the route are only checkable together.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` as JSON. `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns the single value as `int`. It takes no parameters, and `SCHEMA_SQL` does not change.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. It reads no query parameters.
- Do not change `patch_todo`, `delete_todo` or `parse_id`. `"count"` is not a UUID, so the existing 404 path covers AC-900.2.
- `README.md`: add `` - `GET /todos/count` number of todos (`{"count": n}`) `` after the `GET /todos` line, and add `[spec 900](docs/specs/900-count-todos-with-get-todos-count/spec.md)` to the "Details:" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
