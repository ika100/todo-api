# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 2c89bab · **Base:** fb3b4f0 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos (each asserted `201`) on a fresh table (autouse `_fresh_database`), then asserts `200`, `content-type` starting `application/json`, and the parsed body `== {"count": 3}`. The code runs one `SELECT count(*)` and returns `JSONResponse({"count": n})`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:56-61`, `src/todo_api/todos/router.py:72-76` | With an empty table, the test asserts `200` and `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` each assert `404` with the full `todo_not_found` body. `patch_todo` and `delete_todo` are unchanged: `parse_id("count")` is `None`, so they raise `_not_found()`. "Existing endpoints do not change" is covered by the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`). They are unchanged in the diff and green in `devbox run ci`. The only route diff is the added GET handler. |

## Non-goals

No filtering, paging or change to the other endpoints: the router diff adds only `count_todos` (`router.py:40-42`), and `patch_todo`, `delete_todo`, `validation.py` and `errors.py` are unchanged. There is no gitops, configuration, schema (`SCHEMA_SQL` unchanged) or template-owned layout change. ✔

## Deviations from the plan

- `docs/specs/900-.../{design,plan,spec}.md` are in no task's `files`. These are pipeline artifacts (the plan, the design, and the spec status/changelog moving to `building`); acceptable.
- `tests/test_todos_count.py` is in no task's `files`. It holds the acceptance tests, which the plan assigns to the testers before t1; acceptable.
- The only task, t1, is `done: true`. Its files (`repository.py`, `router.py`, `README.md`) match the diff. None.

## Contract

Matches `design.md`. `GET /todos/count` answers `200 application/json {"count": <int>}` with no other fields. The 503 path is the shared `db.run` behaviour. The PATCH/DELETE 404 bodies equal the contract's `todo_not_found` body. The route is declared before the id routes, as the plan says. ✔

## Notes

- `devbox run ci` passed on re-run. The first run had one timing-flaky pre-existing test (`test_unreachable_database_hanging`, 3.3s against a 3s limit). It is not related to this change.
- The acceptance tests are unchanged since the red commit `9db7ddc` (test-diff clean, apart from the lint-fix commit `f2793e2`).

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
