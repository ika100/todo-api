---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "Add GET /todos/count returning {\"count\": n} from one SELECT count(*), without shadowing the PATCH/DELETE id routes"
tasks:
  - id: t1
    title: Add repository.count_todos and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). There is no ADR and no gitops task: the port, the probes, the env vars and the schema do not change.

Levels: t1. This is one task. The repository function is a single query, and splitting it from its only caller would serialize two trivial tasks. The testers write the acceptance tests in a new file before coding, using the existing `tests/conftest.py` harness. No task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`. `PATCH` and `DELETE /todos/count` keep answering `404 todo_not_found` through the existing id handlers.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int`. It runs `SELECT count(*) FROM todos`, reads the single row and returns `int(row[0])`. Raise `RuntimeError` if no row comes back, like `create_todo` does. Use no parameters and do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count")` with handler `count_todos(request: Request) -> JSONResponse`. It calls `await request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Put it directly after `list_todos`, before the `{todo_id}` routes.
- Do not add PATCH or DELETE handlers for `/count`, and do not change `patch_todo`, `delete_todo`, `parse_id` or `parse_patch`. The 404 behaviour in AC-900.2 comes from `parse_id("count")` returning `None`.
- Do not read any query parameters.
- `README.md`: add `` - `GET /todos/count` number of todos (`{"count": n}`) `` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, the existing `tests/` suite passes unchanged (`devbox run test`), and `devbox run quality` and `devbox run security` pass.
