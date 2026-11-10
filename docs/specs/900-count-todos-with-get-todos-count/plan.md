---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: Add GET /todos/count backed by one SELECT count(*), without shadowing the PATCH/DELETE id routes
tasks:
  - id: t1
    title: Add repository.count_todos and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. One task, because the repository function and the route are a few lines each and splitting them would only serialize two tiny tasks. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. There is no migration, and `pyproject.toml`, `Dockerfile`, CI, `docs/env-vars.md` and the gitops repo do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` from a single `SELECT count(*)`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every other endpoint stays as it is.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the integer; raise `RuntimeError` if no row comes back, like `create_todo`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it directly after `list_todos`, above the `/{todo_id}` routes.
- Register GET only. Do not add `PATCH`/`DELETE` handlers or an `api_route` for `/count`; the existing `patch_todo`/`delete_todo` must keep handling `/todos/count` (non-UUID id → `404 todo_not_found`, see design).
- Database errors flow through `Database.run` unchanged (`503 unavailable`); no new error code.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": 3}\`)` after the `GET /todos` line, and add a link to spec 900 next to the spec 002 link.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the unchanged `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
