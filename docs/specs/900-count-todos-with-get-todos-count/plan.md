---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from one SELECT count(*), without shadowing PATCH/DELETE /todos/{id}'
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

Design and contract: [design.md](design.md). No ADR: the decision is local to this feature.

Levels: t1. One task, because the repository function and the route are a few lines each and the route imports the function; splitting them would only serialize two tiny tasks. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. There is no migration, and `pyproject.toml`, `Dockerfile`, CI, `docs/env-vars.md` and the gitops entry do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every existing endpoint behaves as before.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the value as `int`. If `fetchone()` returns `None`, raise `RuntimeError` like `create_todo` does (keeps mypy strict and the branch explicit). Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": count})`. Place it after `list_todos`/`create_todo`, before the `/{todo_id}` handlers.
- Register the route with `GET` only. Do not use `api_route` with extra methods or add any catch-all: `PATCH`/`DELETE /todos/count` must keep falling through to `patch_todo`/`delete_todo`, where `parse_id("count")` gives `404 todo_not_found` (design, Decisions).
- Leave `patch_todo`, `delete_todo`, `list_todos`, `create_todo`, `to_json` and `errors.py` unchanged.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 next to the existing spec links.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
