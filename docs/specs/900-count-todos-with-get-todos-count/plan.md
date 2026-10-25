---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: 'Add GET /todos/count returning {"count": n} from a SELECT count(*), declared before the id routes so it shadows nothing'
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

The contract and the routing decision are in [design.md](design.md). There is no ADR.

Levels: t1. This plan has one task. The testers write the acceptance tests for this spec in a new test file before coding starts, using the existing `tests/conftest.py` harness, and no task edits that file. No task touches the existing test files. The work needs no migration, no gitops change and no config change. `main.py`, `errors.py`, `pyproject.toml`, the `Dockerfile` and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `application/json`. `PATCH`/`DELETE /todos/count` still reach the id routes and answer `404 todo_not_found`. No other endpoint changes.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` that runs `SELECT count(*) FROM todos` and returns the single value as `int`. Use a static SQL string with no parameters. Do not change `SCHEMA_SQL`.
- `router.py`: add `@router.get("/count") async def count_todos(request: Request) -> JSONResponse`. It returns `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Declare it **directly after `create_todo` and before `patch_todo`/`delete_todo`**, so it comes before every `/{todo_id}` route. Register it for GET only. Do not add a `PATCH`/`DELETE` handler on `/count`. Those methods must fall through to the id routes (see design, Decisions).
- Leave `patch_todo`, `delete_todo`, `parse_id` and the error handlers unchanged.
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and link spec 900 next to the existing spec links if such links exist.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass. The existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass unchanged. `devbox run quality` and `devbox run security` pass.
