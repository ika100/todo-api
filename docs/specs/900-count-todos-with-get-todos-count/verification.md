# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 007e9a1 · **Base:** 708cafe · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `::test_count_ignores_query_parameters` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `content-type` starts with `application/json`, body exactly `{"count": 3}` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:56-61`, `:72-76` (unchanged `parse_id` -> `404`) | empty table (autouse `_fresh_database` drops `todos`) asserts `200 {"count": 0}`; `PATCH {"done": true}` and `DELETE /todos/count` assert `404` with the exact `todo_not_found` body. "Existing endpoints do not change": no existing handler is in the diff; `tests/test_todos_api.py` (specs 001, 002) is unchanged and green in the Phase 3 run |

## Non-goals

No filtering, paging, or change to other endpoints (diff of `router.py` adds only the GET `/count` handler; the query parameters test confirms they are ignored, matching the contract). No gitops, configuration or schema change (`SCHEMA_SQL` untouched). No template-owned layout change. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`; acceptable: the plan assigns acceptance tests to the testers before coding, and it was not changed after the red commit (`0ae6150`).
- Spec docs (`spec.md`, `plan.md`, `design.md`) are outside task files; acceptable: pipeline status and planning artefacts.
- Task t1 is `done: true`. No other deviation.

## Contract

Matches `design.md`: `200 application/json {"count": n}` with exactly one key, via `db.run` (same `503` mapping as `GET /todos`), `SELECT count(*) FROM todos` with no user input, GET-only route declared before the `/{todo_id}` routes. The `503` and `405` contract lines are not asserted by spec 900 tests (they are not criteria); behaviour is inherited from existing code. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
