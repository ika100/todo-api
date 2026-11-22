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

Contract: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. One task, because the query and the route that makes the acceptance tests pass cannot pass alone. The acceptance tests are written by the testers before coding, using the existing `tests/conftest.py` harness; no task edits them, nor `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. No migration, no config, no gitops change; `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`; `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found`; every other endpoint behaves as before.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the single value as `int` (raise `RuntimeError` if no row, like `create_todo`). Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count") async def count_todos(request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Go through `db.run` so the deadline and the `503 unavailable` mapping apply unchanged.
- Do not add `PATCH`/`DELETE` handlers for `/count` and do not change `patch_todo`/`delete_todo`: they already map the non-UUID id `count` to `404 todo_not_found` (design, Decisions).
- `README.md`: add the line ``- `GET /todos/count` count the todos (`{"count": n}`)`` after the `GET /todos` line, and a link to spec 900 next to the spec 002 link.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
