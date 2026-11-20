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

Contract and decisions: [design.md](design.md). There is no ADR, no migration, and no gitops, configuration, `pyproject.toml` or `Dockerfile` change. The acceptance tests for AC-900.1 and AC-900.2 are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, and no task touches `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`.

One task: the query and the route that makes its tests pass belong together, and the change is too small to split.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` as `application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` through the unchanged id routes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the value as `int`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` handler `count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Place it next to `list_todos`.
- Do not add a `GET /{todo_id}` route and do not change `patch_todo` or `delete_todo`: their `parse_id` already turns `count` into `404 todo_not_found` (design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
