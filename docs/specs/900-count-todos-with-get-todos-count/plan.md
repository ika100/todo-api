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

Design and contract: [design.md](design.md). There is no ADR, because every decision is local to this feature. There is no gitops, configuration or schema change (non-goal).

Levels: t1. This is one task because the repository function and the route are a few lines each. Splitting them would only serialize two tiny tasks. The testers write the acceptance tests for this spec in a new file before coding, using the existing `tests/conftest.py` harness. No task edits them. `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` stay unchanged and must keep passing.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`. `PATCH`/`DELETE /todos/count` still answer `404 todo_not_found`, and the other endpoints do not change.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns the integer. Fail loudly like `create_todo` if no row comes back. Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count")` `async def count_todos(request: Request) -> JSONResponse` that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. Pass a Python `int` so the body is a JSON integer.
- Do not add `PATCH`/`DELETE` handlers for `/count`, and do not special-case `"count"` in `parse_id`. The existing `/{todo_id}` routes already give the required 404 (design, Decisions).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and link spec 900 next to the existing spec links if there are any.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, together with the unchanged `tests/test_todos_api.py` and `tests/test_todos_title_patch.py`, under `devbox run test`. `devbox run quality` and `devbox run security` also pass.
