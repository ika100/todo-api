# Verification — 900 Count the todos with GET /todos/count

**Commit:** 67c6900 · **Base:** c472dec · **Trace:** 2/2 criteria named by tests (none missing)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-42`, `src/todo_api/todos/repository.py:38-43` | Creates 3 todos (each asserted 201), asserts status 200, `content-type` starting with `application/json`, decoded body `== {"count": 3}`, and an `int` count. The count comes from `SELECT count(*) FROM todos` as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_count_does_not_shadow_patch`, `::test_count_does_not_shadow_delete` | `src/todo_api/todos/router.py:40-42` (static GET only); unchanged `router.py:56` (PATCH), `router.py:72` (DELETE), `validation.py:67` (`parse_id("count")` gives `None`), `router.py:30-31` (`_not_found`) | Empty DB (autouse `_fresh_database` drops the table) gives 200 `{"count": 0}`. PATCH with `{"done": true}` and DELETE on `/todos/count` give 404 with the exact `todo_not_found` body; the message matches `MSG_TODO_NOT_FOUND` (`src/todo_api/errors.py:16`). "Existing endpoints do not change": the diff adds lines only and changes no handler, and the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass in the green `devbox run ci`. |

## Non-goals

No filtering, paging, query parameters or changes to other endpoints. No gitops, configuration or schema changes: the diff touches only `repository.py`, `router.py`, the new test file and the spec documents. No template-owned files changed. ✔

## Deviations from the plan

- Task t1 is `done: true`. Its `files` (`repository.py`, `router.py`) match the code changes. The only other files are `tests/test_todos_count.py` (the red-phase acceptance tests) and the spec's own `design.md`, `plan.md` and `spec.md` (a status change to `building` plus a changelog line). Acceptable: these are pipeline artifacts.
- None in the implementation. It follows the plan's notes word for word (`RuntimeError` on a missing row, `JSONResponse` through `db.run`, no extra error handling).

## Contract

Matches `design.md`: `GET /todos/count` returns 200 `application/json` with a body that has the single key `count`, an int. Database errors go through `db.run` to the global 503 `unavailable` handler, as for the other endpoints. PATCH and DELETE on `/todos/count` keep the existing 404 `todo_not_found`. ✔

## Notes

- `cplat spec test-diff` reports that no acceptance test changed after the red commit. There are no suppressions, no tightened tests and no unresolved test-review findings.
- `tests/test_todos_api.py::test_unreachable_database_hanging` is a known flaky test that predates this spec. It passed on rerun and is unrelated to it.

**Result:** pass
