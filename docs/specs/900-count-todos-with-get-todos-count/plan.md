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
---

# Plan — 900 Count the todos with GET /todos/count

Contract and routing reasoning: [design.md](design.md). No ADR: every decision is local to this feature.

Levels: t1. One task: the repository function and the route are a few lines each and the route is useless without the query, so splitting them would only serialize work. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. No migration, no gitops, no config change; `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`, and `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` like any unknown id.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning `int(row[0])`; raise `RuntimeError` if `fetchone()` returns `None`, like `create_todo`. Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` returning `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Place it directly after `list_todos`, before the `/{todo_id}` routes.
- Leave `patch_todo` and `delete_todo` unchanged: `parse_id("count")` already yields `None` → `404 todo_not_found` (design, Decisions).
- `README.md`: after the `GET /todos` line, add the endpoint line "GET /todos/count: number of todos as {"count": n}" in the list's existing style, and add a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, every existing test passes unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
