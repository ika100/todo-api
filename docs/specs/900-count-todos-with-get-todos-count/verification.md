# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 5b7b24c · **Base:** 75d61de · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `Content-Type` starting `application/json`, body exactly `{"count": 3}`; count computed with `SELECT count(*)` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_count_route_does_not_shadow_id_routes`, `::test_existing_endpoints_unchanged_by_count` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57`, `src/todo_api/todos/router.py:73` | empty DB (per-test drop in `tests/conftest.py`) gives `{"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` assert `404` with the exact `todo_not_found` body (`src/todo_api/errors.py:16`), via untouched `parse_id` path; PATCH/DELETE/GET/POST handlers unchanged in the diff and the existing suite passes |

## Non-goals

No filtering, paging, or change to other endpoints; no gitops, configuration or schema change. No template-owned layout touched. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`; acceptable, it is the acceptance test file written before the build.
- `count_todos` raises `RuntimeError` when `fetchone()` returns `None` (not in the design pseudocode); acceptable, a type-narrowing guard that `count(*)` never triggers.

All tasks (`t1`) are `done: true`.

## Contract

Matches `design.md`: `GET /todos/count` returns `200` `{"count": n}` with exactly one key; `503` handled by the existing `db.run` `DatabaseUnavailable` path (no dedicated test, not an acceptance criterion). ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
