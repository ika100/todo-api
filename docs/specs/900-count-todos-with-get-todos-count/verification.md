# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 6265ab0 · **Base:** 361779a · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:50` | Creates three todos through the API, then asserts `200`, `content-type` starting with `application/json`, and body equal to `{"count": 3}` (an exact dict, so exactly one key). The count runs in the database as `SELECT count(*) FROM todos` (`repository.py:51`), as `design.md` requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`; existing `router.py:57-62` and `router.py:73-77` (unchanged) | Empty database (the autouse `_fresh_database` fixture drops `todos` before each test, `tests/conftest.py:74`): asserts `200` and `{"count": 0}`. With one todo stored, `PATCH /todos/count` `{"done": true}` and `DELETE /todos/count` both return `404` with the exact `todo_not_found` body, and the stored todo is still there afterwards. For "existing endpoints do not change": the diff of `router.py` and `repository.py` only adds lines (+6 and +8, no lines removed), and the existing suite passes in the green `devbox run ci`. |

## Non-goals

No filtering, paging, query parameters or changes to other endpoints: the handler takes no parameters (`router.py:41`). No schema, configuration or gitops change: `SCHEMA_SQL` is untouched and no config or deploy files are in the diff. ✔

## Deviations from the plan

- t1 has `done: true`. Every source file changed (`repository.py`, `router.py`) is in t1's `files`. `tests/test_todos_count.py` comes from the acceptance-test commit and the `docs/specs/900-*` files are spec artifacts, so both are expected. None.
- One small difference: `count_todos` uses `conn.execute(...)` directly instead of the `conn.cursor(row_factory=...)` style of its neighbours. It matches `delete_todo` (`repository.py:73`), keeps the `RuntimeError` on a missing row as the plan asks (`repository.py:53-54`) and changes no behaviour. Acceptable.

## Contract

Matches `design.md`: literal `GET /todos/count` on the existing router, declared before the `/{todo_id}` routes, `200 {"count": <int>}` as JSON, no new error code. `503` goes through the existing `DatabaseUnavailable` handler via `request.app.state.db.run`, the same way as `GET /todos` (`router.py:36` and `router.py:42`). No test covers the 503 for `/count`, but no acceptance criterion requires it. PATCH and DELETE handlers are unchanged. ✔
