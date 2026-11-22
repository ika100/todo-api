# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** e2df5e3 · **Base:** 2be19b4 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-44` | Creates 3 todos (each asserted 201), asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` (exact, one key). |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id` | `src/todo_api/todos/router.py:40-43` (GET), `src/todo_api/todos/router.py:57-62`, `:73-77` (unchanged id routes, `parse_id("count")` is `None`) | Empty DB (autouse `_fresh_database` in `tests/conftest.py`) gives `200` `{"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` give `404` with the exact `todo_not_found` body. Each shadowing test first asserts GET `/todos/count` is `200`, so it cannot pass without the route. "Existing endpoints do not change": the diff touches no existing handler; the existing suite passes (`devbox run ci` green). |

## Non-goals

No filtering, paging, or change to other endpoints: the router diff adds only the `GET /count` handler. No gitops, configuration or schema change: no such files in the diff. No template-owned files touched. ✔

## Deviations from the plan

- `tests/test_todos_count.py` and `tests/unit/test_db_internals.py` are in no task's `files`; acceptable: acceptance tests and unit tests for the new `count_todos` (covers the `RuntimeError` branch the plan asks for).
- Task t1 has `done: true`. No other deviations.

## Contract

Matches `design.md`: `SELECT count(*) FROM todos` (not `len(list_todos())`), body has exactly one key `count`, DB access runs inside `db.run` so an unreachable database maps to the existing `503 unavailable`. The 503 path for `/todos/count` is not covered by an acceptance test, but it is no acceptance criterion and reuses the shared `db.run` handler. ✔

## Mutation check (report only)

1 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

1 of 1 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
