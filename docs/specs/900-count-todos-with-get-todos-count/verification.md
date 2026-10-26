# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 3938306 · **Base:** bc7c808 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count_api.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos through `POST /todos`, asserts `200`, `content-type` starts with `application/json`, and body `== {"count": 3}`. The count runs as `SELECT count(*) FROM todos` in Postgres, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count_api.py::test_count_empty_and_no_shadowing` | `src/todo_api/todos/router.py:40` (GET only); `router.py:57`, `router.py:73` unchanged | Asserts `{"count": 0}` on an empty table. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both return `404` with the exact `todo_not_found` body. `parse_id("count")` returns `None`, so `_not_found()` is raised at `router.py:62` and `router.py:77`. "Existing endpoints do not change": the diff does not touch the existing handlers or tests, and the existing suite passes in `devbox run ci`. |

## Non-goals

No filtering, paging, schema, config or gitops change was added. The diff touches only `repository.py` (+8), `router.py` (+6) and the new test file. ✔

## Deviations from the plan

- `tests/test_todos_count_api.py` is listed in no task's `files`. This is acceptable: it is the red-first acceptance test commit (57c9ce2), which comes before the task.
- Task t1 is `done: true`. No other deviations.

## Contract

Matches `design.md`: `GET /todos/count` returns `200 {"count": <int>}` as `application/json` through `JSONResponse`, and the result is a Python `int` (`repository.py:43`). A database failure goes through the existing `db.run` → `DatabaseUnavailable` → `503` mapping, with no new error handling. The route is declared before the `/{todo_id}` routes. The 503 path has no test for this endpoint specifically, but the spec does not make it a criterion. ✔
