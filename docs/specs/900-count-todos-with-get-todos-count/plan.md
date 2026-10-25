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

Design and contract: [design.md](design.md). No ADR: every decision is local to this feature.

Levels: t1. One task: the route imports the new repository function, and the whole change is a few lines, so splitting it would only serialize two tiny tasks. The acceptance tests are written by the testers in a new file before coding and no task edits them. No migration, no configuration, no gitops change; `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.count_todos and the GET /todos/count route

**Files:** src/todo_api/todos/repository.py, src/todo_api/todos/router.py, README.md
**Covers:** AC-900.1, AC-900.2
**Goal:** `GET /todos/count` answers `200 {"count": n}` with `Content-Type: application/json`, while `PATCH`/`DELETE /todos/count` keep answering `404 todo_not_found` and every existing endpoint is unchanged.

**Implementation notes:**
- `repository.py`: add `async def count_todos(conn: AsyncConnection) -> int` running `SELECT count(*) FROM todos` and returning the integer (`fetchone()`; a missing row is a `RuntimeError`, as in `create_todo`). Do not change `SCHEMA_SQL` or the other queries.
- `router.py`: add `@router.get("/count")` handler returning `JSONResponse({"count": await request.app.state.db.run(repository.count_todos)})`. Register only `GET`. Do not touch `patch_todo` or `delete_todo`; they already answer `404 todo_not_found` for the non-UUID id `count`.
- Name the handler so it does not clash with the imported module function (e.g. `count_todos` in the router is fine since the repository is referenced as `repository.count_todos`).
- `README.md`: add `- \`GET /todos/count\` number of todos (\`{"count": n}\`)` after the `GET /todos` line, and a link to spec 900 next to the existing spec links.

**Done when:** the AC-900.1 and AC-900.2 acceptance tests pass, the whole existing test suite passes unchanged with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
