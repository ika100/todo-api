# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 76c4dba · **Base:** 66dadd0 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-43` | Creates three todos (each asserted `201`), asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` (exact, one key). Count is computed by `SELECT count(*) FROM todos`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` | Fresh database (autouse `_fresh_database` drops the table) gives `200` `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both asserted `404` with the full `todo_not_found` body `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. The `/{todo_id}` handlers are untouched; `parse_id("count")` yields `None` and raises `_not_found()`. "Existing endpoints do not change": the diff only adds code to `router.py`/`repository.py`, no existing test changed, and the full suite is green (`devbox run ci`). |

## Non-goals

No filtering, paging or query parameters; no change to the other endpoints (diff is additive only); no gitops, configuration or schema change; no template-owned files touched. ✔

## Deviations from the plan

None. Code changes are limited to t1's `files` (`src/todo_api/todos/repository.py`, `src/todo_api/todos/router.py`); `tests/test_todos_count.py` is the acceptance test file and the `docs/specs/900-*` files are the spec artefacts. t1 is `done: true`.

## Contract

Matches `design.md`: `GET /todos/count` returns `200` `{"count": <int>}` via `db.run` (so the existing `503 unavailable` path applies); `PATCH`/`DELETE /todos/count` answer `404 todo_not_found`. ✔

## Test review

The reviewed-acceptance-tests commit (756898f) records `findings: 0`; no unresolved test-review findings. No suppressions and no tightened tests in this build.

## Smoke

None: both tests assert exact bodies that only the feature (or the existing id handlers, for the 404 checks) can produce.

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
