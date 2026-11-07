# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** b60c0aa · **Base:** 24c98a2 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/repository.py:38` | Test creates three todos via `POST /todos`, asserts `200`, `content-type` starts with `application/json` and body equals exactly `{"count": 3}`. Count is computed in the DB with `SELECT count(*) FROM todos` (`repository.py:39`), as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:51` (GET only), unchanged `router.py:57` (`patch_todo`), `router.py:73` (`delete_todo`) | Empty DB gives `200` `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both asserted `404` with the full `todo_not_found` body; the test also asserts GET returns 200 first, so the 404s are not caused by a missing route. "Existing endpoints do not change": the diff only adds lines to `router.py`; existing endpoint tests pass in `cplat quiet ci`. |

## Non-goals

No filtering, paging or query parameters on the count route; no change to other endpoints (router diff is additive only). No gitops, configuration or schema change (no migration, config or `main.py` touched). ✔

## Deviations from the plan

- None. Source changes are limited to t1's `files` (`repository.py`, `router.py`); `tests/test_todos_count.py` is the acceptance test file and the spec docs are pipeline artifacts. t1 is `done: true`.
- Count route is declared before the `/{todo_id}` routes (`router.py:51` vs `:57`, `:73`), as the plan asks.

## Contract

Matches `design.md`: `GET /todos/count` returns `200` `application/json` `{"count": <int>}` with exactly one key; DB access goes through `app.state.db.run` (`router.py:53`), so the `503 unavailable` path is the existing `DatabaseUnavailable` handling (not covered by an acceptance test, and not an acceptance criterion). `repository.count_todos` raises `RuntimeError` on a missing row as the plan states (`repository.py:41-42`). ✔

## Notes

- Unrelated flaky test `test_unreachable_database_hanging` (spec 001) failed once in `test-fast` and passed on re-run; not touched by this change.

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
