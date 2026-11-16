# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** d91c32c · **Base:** 72e7c35 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `Content-Type` starting with `application/json`, body `== {"count": 3}`; count computed in the DB with `SELECT count(*)` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57`, `src/todo_api/todos/router.py:73`, `src/todo_api/todos/validation.py:67` | empty DB (autouse `_fresh_database`) gives `200 {"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` asserted `404` with the exact `todo_not_found` body; `parse_id("count")` returns `None` so the unchanged id handlers answer `404`. "Existing endpoints do not change": diff touches no existing handler, and `tests/test_todos_api.py` / `tests/test_todos_title_patch.py` pass unchanged in the green run |

## Non-goals

No filtering, paging, query parameters, or change to other endpoints; no gitops, configuration or schema change. No template-owned layout changes. ✔

## Deviations from the plan

None. Code changes are confined to t1's `files` (`repository.py`, `router.py`); the only other changed files are the acceptance test and the spec docs. t1 is `done: true`.

## Contract

Matches `design.md`: `GET /todos/count` -> `200` `{"count": n}` via `JSONResponse`; `503 unavailable` path inherited from `db.run` unchanged; `PATCH`/`DELETE /todos/count` -> `404 todo_not_found`. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
