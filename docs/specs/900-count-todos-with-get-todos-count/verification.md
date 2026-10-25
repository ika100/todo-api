# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 52d88c6 · **Base:** 0a663fc · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates 3 todos through `POST /todos` against the real Postgres (`tests/conftest.py:90`), asserts `200`, `Content-Type` starting with `application/json`, and body exactly `{"count": 3}`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_patch_count_is_todo_not_found`, `::test_delete_count_is_todo_not_found` | `src/todo_api/todos/router.py:40` (GET only); unchanged `router.py:57-62` (PATCH) and `router.py:73-77` (DELETE) return `_not_found()` for the non-UUID id `count` | Empty table gives `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404`, JSON, single `error` key, code `todo_not_found` and message `This todo no longer exists` (= `MSG_TODO_NOT_FOUND`, `src/todo_api/errors.py:16`). "Existing endpoints do not change": the router diff only adds lines 40-43; `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are untouched and pass (164 passed). |

Acceptance tests are unchanged since the red commit `222493e` (`git diff 222493e..HEAD -- tests/test_todos_count.py` is empty).

## Non-goals

No filtering, paging or query-parameter handling was added; no other endpoint changed (router diff is additive only). No gitops, configuration (`docs/env-vars.md`, settings) or schema (`SCHEMA_SQL`) change. ✔

## Deviations from the plan

- `tests/unit/test_db_internals.py` changed but is in no task's `files`: adds `test_count_todos_without_row_raises` covering the `RuntimeError` branch the plan's t1 asked for. Acceptable: a unit test for an internal branch, no production impact.
- `docs/specs/900-.../spec.md` status line (`building`) and `plan.md` `done` flags changed by the orchestrator: acceptable, pipeline bookkeeping.
- All tasks (t1, t2) are `done: true`.

## Contract

Matches `design.md`: `GET /todos/count` returns `JSONResponse({"count": n})` with exactly one key; the count runs as one `SELECT count(*) FROM todos` through `Database.run` (`router.py:42`, `repository.py:39`), so database errors and the deadline go through the same `503 unavailable` mapping as `GET /todos`. Only GET is registered on `/count`; `patch_todo` and `delete_todo` are unchanged. `count_todos(conn: AsyncConnection) -> int` signature matches. README lists the endpoint and links spec 900 as planned. ✔

Observation (not a failure): the 503 path for `GET /todos/count` has no dedicated test; it is contract-only (no criterion states it) and reuses the shared `Database.run` error mapping.
