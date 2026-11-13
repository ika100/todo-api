# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 6744177 · **Base:** fc90edb · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `application/json`, body exactly `{"count": 3}`; count runs as `SELECT count(*) FROM todos` as the design asks |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` (unchanged `parse_id` -> `todo_not_found`) | asserts `{"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` give `404` with exactly `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. "Existing endpoints do not change": the diff leaves the existing handlers and `tests/test_todos_api.py` untouched and that suite passes (`devbox run ci` green) |

## Non-goals

No filtering, paging, or change to the other endpoints; no gitops, configuration or schema change. No template-owned layout touched. ✔

## Deviations from the plan

None. Every changed file is in t1's `files` (`repository.py`, `router.py`, `README.md`) or is the acceptance test / spec docs; t1 is `done: true`. Acceptance tests were not changed after the review commit `11c1ca0` (the feature commit `e3decbb` touches only source and README).

## Contract

Matches `design.md`: `GET /todos/count` -> `200` `{"count": n}` as JSON; the `503 unavailable` path is inherited via `request.app.state.db.run`, like the other routes; PATCH/DELETE on `/todos/count` keep the existing `404 todo_not_found`. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
