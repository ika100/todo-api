# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 1c7e49b · **Base:** 7585af4 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Asserts status `200`, `content-type` starting with `application/json`, and body equal to `{"count": 3}` after three `POST /todos` (each asserted `201`). Count comes from `SELECT count(*) FROM todos` through `db.run`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_zero_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:56`, `src/todo_api/todos/router.py:72` (unchanged id routes) | Asserts `200 {"count": 0}` with no todos; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` with the exact `todo_not_found` body. "Existing endpoints do not change": the diff only adds lines to `router.py`/`repository.py`, no existing handler, test or error is modified, and the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) pass in the reported CI run. |

## Non-goals

No filtering, paging, schema, configuration or gitops change; no other endpoint touched. No template-owned layout change (service has no UI). ✔

## Deviations from the plan

None. The changed source files (`repository.py`, `router.py`) are exactly t1's `files`; t1 is `done: true`. `tests/test_todos_count.py` holds the acceptance tests, and `spec.md`, `plan.md`, `design.md` are spec artefacts. Implementation follows the plan notes: `RuntimeError` on no row, GET only, no special case for `count`.

## Contract

Matches `design.md`: `200` JSON `{"count": <int>}` with no other fields; `503 unavailable` is inherited through `request.app.state.db.run` like `GET /todos` (not tested by the acceptance tests, and no criterion requires it). `PATCH`/`DELETE /todos/count` return the existing `404 todo_not_found`. ✔

## Mutation check (report only)

2 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

2 of 2 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
