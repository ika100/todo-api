# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** b5fa027 · **Base:** 956a711 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | The test creates three todos through `POST /todos` (each asserted 201), then asserts status 200, a `Content-Type` starting with `application/json` and the exact body `{"count": 3}`. The count comes from Postgres with `SELECT count(*) FROM todos` (`repository.py:39`), not from loading the list, as `design.md` requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes`, existing suite `tests/test_todos_api.py` | `src/todo_api/todos/router.py:40` (GET only), `router.py:57-62` and `router.py:73-77` (unchanged id routes, `parse_id("count")` gives `None`, then `_not_found()`) | Empty case: the autouse `_fresh_database` fixture (`tests/conftest.py`) drops `todos` before each test; the test asserts 200, a JSON content type and `{"count": 0}`. Shadowing: the test first checks that `GET /todos/count` is 200, so a missing route cannot make it pass by accident. It then sends `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` and expects 404 with the exact `todo_not_found` body, which matches `MSG_TODO_NOT_FOUND` (`src/todo_api/errors.py:16`). Existing endpoints unchanged: the diff only adds code and changes no existing handler, and the AC-001.* suite passes (per the phase 3 `devbox run ci` run). |

## Non-goals

There is no filtering, no paging and no change to the other endpoints. The diff to `router.py` is one new handler, and the diff to `repository.py` is one new function. There is no gitops, configuration or schema change: the new query reads the existing `todos` table. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: it is the acceptance-test file, committed red-first in `1be7719` before the implementation in `9a9b0df`.
- Task t1 is `done: true`. No other files changed outside the plan, apart from the spec docs.

## Contract

The build matches `design.md`:
- `GET /todos/count` returns `JSONResponse({"count": n})`, which is a 200 with `application/json` (`router.py:43`).
- `count_todos(conn: AsyncConnection) -> int` has the signature the design gives and raises `RuntimeError` when no row comes back (`repository.py:38-43`).
- Only `GET` is registered on `/count`, and there is no 405 handler.
- A 503 on an unreachable database comes from the shared `app.state.db.run` path (`router.py:42`), the same path `GET /todos` uses. No test covers it for `/count`, but no criterion requires one; it is a gap to note, not a failure. ✔
