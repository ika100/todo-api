---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "Add GET /todos/count returning a count from one SELECT count(*), without shadowing the /todos/{id} routes"
tasks:
- id: t1
  title: Add repository.count_todos and the GET /todos/count route
  files: [src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md]
  covers: [AC-900.1, AC-900.2]
  parallel_safe: true
  depends_on: []
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). No ADR: the decision is local to this endpoint.

Levels: t1. One task: the route imports the query, and both are a few lines, so splitting would only serialize two tiny tasks. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or `tests/test_todos_title_patch.py`. No migration, no gitops, configuration, `pyproject.toml`, `Dockerfile` or CI change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` through the unchanged id routes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the integer (`fetchone()[0]`; raise `RuntimeError` if no row, like `create_todo`). Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` declared directly after `list_todos` and before `patch_todo`/`delete_todo`. It runs `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Database errors propagate unchanged so the existing `503 unavailable` mapping applies.
- Docstring on the handler: any future `GET /todos/{todo_id}` must be declared after this route.
- Do not touch `patch_todo` or `delete_todo`: the 404 for `count` comes from `parse_id` returning `None` (design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 in the "Details" line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and all existing tests pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
