---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from a SQL count, without shadowing PATCH/DELETE /todos/{id}'
tasks:
  - id: t1
    title: Add repository.count_todos and the GET /todos/count route
    files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
    covers: [AC-900.1, AC-900.2]
    parallel_safe: true
    depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). No ADR: the decision is local to this feature.

Levels: t1. One task, because the repository function and the route are a few lines each and the route cannot be tested without the query; splitting would only serialize two tiny tasks. The acceptance tests are written by the testers in a new file (e.g. `tests/test_todos_count.py`) before coding, with the existing `tests/conftest.py`; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. No migration, and `pyproject.toml`, `Dockerfile`, CI, `docs/env-vars.md` and the gitops repo do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every existing endpoint is unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running the constant statement `SELECT count(*) FROM todos` and returning the single value as `int` (raise `RuntimeError` if no row, like `create_todo`). Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Declare it directly after `list_todos`, above the `/{todo_id}` routes.
- Register only `GET` on `/count`. Do not add `PATCH`/`DELETE` handlers or any special case for `"count"` in `patch_todo`, `delete_todo` or `parse_id`: the existing non-UUID path already yields `404 todo_not_found` (design, Decisions).
- Database errors propagate as today (`DatabaseUnavailable` → `503 unavailable`); no new error handling.
- `README.md`: add `- GET /todos/count` "count all todos (`{"count": n}`)" after the `GET /todos` line, and a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
