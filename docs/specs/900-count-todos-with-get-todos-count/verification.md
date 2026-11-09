# Verification — 900 Count the todos with GET /todos/count

**Commit:** 4c87aa3 · **Base:** 8307043 · **Trace:** 2/2 criteria named by tests (`missing: []`)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `::test_count_follows_deletes` | `src/todo_api/todos/router.py:40-42`, `src/todo_api/todos/repository.py:38-43` | Creates three todos, asserts `200`, `Content-Type` starting with `application/json`, decoded body `== {"count": 3}` and that `count` is an `int`. The second test shows the count follows a delete (2 then 1). The count is one `SELECT count(*) FROM todos` (repository.py:39) and the list is never loaded. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `::test_count_does_not_shadow_id_routes`, `::test_count_route_leaves_existing_endpoints_unchanged` | `src/todo_api/todos/router.py:40-42`; unchanged `router.py:56-61` (`patch_todo`), `router.py:72-76` (`delete_todo`) | Empty DB: `200`, JSON, `{"count": 0}`, int. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` and the exact `todo_not_found` body. The route is GET-only, so PATCH/DELETE reach the id handlers, where `parse_id("count")` is `None` and returns 404. "Existing endpoints do not change": the diff does not touch `list_todos`, `create_todo`, `patch_todo` or `delete_todo`, the unchanged spec 001/002 suites pass (`devbox run ci` green), and `GET /todos` still returns the created todo. |

## Non-goals

There is no filtering, paging or change to any other endpoint (the router diff only adds lines 40-42). No gitops, configuration, schema or migration change: `SCHEMA_SQL` is untouched and the diff contains no config files. No template-owned layout changed. ✔

## Deviations from the plan

None. Every changed file is in a task's `files`: `repository.py` (t1), `router.py` and `README.md` (t2), the new acceptance test file (the tester's red commit `5bc9816`), plus spec docs. Both tasks are `done: true`. The README matches t2's notes: the endpoint line comes after `GET /todos`, and the "Details" line links spec 900.

## Contract

The build matches `design.md`. The response is `200 {"count": <int>}` with exactly one key (the tests compare the whole decoded body) and `application/json`. The handler goes through `db.run`, so a missed DB deadline gets the same `503 unavailable` mapping as the other routes. PATCH/DELETE on `/todos/count` answer `404 todo_not_found` as stated. `count_todos(conn: AsyncConnection) -> int` has the specified signature and raises `RuntimeError` on a missing row, as the plan says. No test covers the 503 and `POST /todos/count → 405` lines of the contract. These lines are not acceptance criteria, and the existing shared mechanisms provide them. ✔

**Result:** pass

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
