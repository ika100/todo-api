# Verification — 900 Count the todos with GET /todos/count

**Commit:** 1b03d71 · **Base:** fbe70e9 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | The test creates three todos, then asserts `200`, `content-type` starts with `application/json`, and the decoded body `== {"count": 3}` (exact dict, so exactly one key). The count runs in Postgres via `SELECT count(*) FROM todos` through `db.run`, as `design.md` specifies. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_none_and_no_shadowing` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57`, `src/todo_api/todos/router.py:73` | The autouse `_fresh_database` fixture (`tests/conftest.py`) drops `todos` before each test, so the test starts with no todos. It asserts `200` with `{"count": 0}`, then `PATCH /todos/count` `{"done": true}` and `DELETE /todos/count` each give `404` with the exact `todo_not_found` body. The id routes are unchanged: `parse_id("count")` returns `None`. "Existing endpoints do not change": the diff only adds code in `router.py`/`repository.py`, and the existing suite passes under `devbox run ci`. |

## Non-goals

- No filtering, paging, or change to other endpoints: the router diff adds the `/count` handler and nothing else. ✔
- No gitops, configuration or schema change: no migration, no new env var. The only non-plan change is a comment in `db.py`. ✔
- No template-owned layout changes (not applicable to an API service). ✔

## Deviations from the plan

- `src/todo_api/db.py` changed but is in no task's `files`. Commit `811b6d6` only shortens the `OP_DEADLINE_S` comment to clear an E501 lint failure that already existed on main and blocked the quality gate. The value stays `2.0` and behaviour does not change. Acceptable.
- All tasks (`t1`) are `done: true`. ✔

## Contract

Matches `design.md`: `GET /todos/count` returns `200 {"count": n}` through `JSONResponse`. The repository signature is `count_todos(conn: AsyncConnection) -> int`. An unreachable database gives the existing `503 unavailable` through `db.run`. No new error codes. ✔

## Notes

- The Phase 3 CI run had one flake on its first attempt: `tests/test_todos_api.py::test_create_invalid_request`, an existing test, hit a container timing problem. It passed on re-run and on its own. This feature did not touch that test.
- Suppressions: none. Tightened tests: none. Unresolved test-review findings: none.

**Result:** pass

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
