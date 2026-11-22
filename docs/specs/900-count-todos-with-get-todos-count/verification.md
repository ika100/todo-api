# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 4c47315 · **Base:** 78580e8 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-43` | Creates three todos (each asserted 201), asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` and the value is an int, not a bool. Count runs `SELECT count(*) FROM todos` in the database. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_count_does_not_shadow_patch`, `::test_count_does_not_shadow_delete` | `src/todo_api/todos/router.py:40-43`; existing `router.py:57-62` and `router.py:73-77` (`parse_id("count")` is `None`, so `_not_found()`) | Empty DB is guaranteed by the autouse `_fresh_database` fixture (`tests/conftest.py`); asserts `200` with body `== {"count": 0}`. PATCH with `{"done": true}` and DELETE assert `404` and the exact `todo_not_found` body. "Existing endpoints do not change": the diff touches no existing handler, and the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) pass in `devbox run ci`. |

## Non-goals

No filtering, paging or query parameters; no change to any other endpoint (the diff adds only the new handler and the repository function). No gitops, configuration or schema change. No template-owned layout touched. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is outside task t1's `files`; acceptable: it is the acceptance test file written in the test-first phase.
- `repository.count_todos` raises `RuntimeError` when `fetchone()` returns `None`, which the design pseudocode does not have; acceptable: a typing guard for an impossible case (`count(*)` always returns one row).
- Task t1 is `done: true`. Every screen/state check is N/A (no `ux.md`, API-only service).

## Contract

Matches `design.md`: `GET /todos/count` → `200 {"count": <int>}` as `application/json`; database errors go through `app.state.db.run` (existing 503 handler); no PATCH/DELETE handlers were added for `/count`; the route is declared directly after `list_todos`. ✔

## Mutation check (report only)

0 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

No mutant was tested: the acceptance tests alone used the time budget (spec 152, report only).
