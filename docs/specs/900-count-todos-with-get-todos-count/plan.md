---
spec_id: 900-count-todos-with-get-todos-count
shape: service-python
spec_hash: 44aaaeaf0c84
summary: "GET /todos/count answers {\"count\": n} from one SELECT count(*), without shadowing PATCH/DELETE /todos/{id}"
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

Design and contract: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1. One task, because the query and the route that makes the acceptance tests pass cannot be checked apart. The acceptance tests are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness; no task edits them, `tests/test_todos_api.py` or any other existing test. There is no migration, and `pyproject.toml`, `Dockerfile`, CI, `docs/env-vars.md` and the gitops repo do not change (spec non-goals).

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, counted in Postgres, while `PATCH /todos/count` and `DELETE /todos/count` keep answering `404 todo_not_found` through the existing id handlers.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` (no parameters) and returning the value as `int`. Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` (handler name e.g. `count_todos`), placed after `create_todo` and before `patch_todo`, that calls `request.app.state.db.run(repository.count_todos)` and returns `JSONResponse({"count": n})`. No other fields.
- Do not add `PATCH`/`DELETE` handlers on `/count` and do not touch `patch_todo`, `delete_todo`, `parse_id` or `errors.py`: Starlette's full-match-over-partial-match routing already sends those methods to the id handlers (design, Decisions).
- Errors go through `Database.run` unchanged, so an unreachable database answers the existing `503 unavailable`.
- `README.md`: add `- GET /todos/count` "number of todos (`{"count": n}`)" under `## API`, after `GET /todos`, and add a link to spec 900 next to the spec 002 link.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests and the whole unchanged existing test suite pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
