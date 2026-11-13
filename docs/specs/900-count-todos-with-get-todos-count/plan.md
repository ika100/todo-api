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
  done: true
---

# Plan — 900 Count the todos with GET /todos/count

Design and contract: [design.md](design.md). There is no ADR, because every decision is local to this feature.

Levels: t1. One task, because the repository function and the route that makes the acceptance tests pass cannot be checked apart. The testers write the AC-900 acceptance tests in a new file before coding, using the existing `tests/conftest.py` harness. No task edits those tests. There is no migration, and the config, `pyproject.toml`, `Dockerfile`, CI and gitops stay as they are.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`. `PATCH` and `DELETE /todos/count` still answer `404 todo_not_found`.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns the single value as `int`. Raise `RuntimeError` if no row comes back, as `create_todo` does. Leave `SCHEMA_SQL` and the other queries unchanged.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse` that returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Put it right after `list_todos`, before the `/{todo_id}` routes.
- Do not change `patch_todo`, `delete_todo`, `validation.py` or `errors.py`. Their current behaviour gives the AC-900.2 404s (see design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
