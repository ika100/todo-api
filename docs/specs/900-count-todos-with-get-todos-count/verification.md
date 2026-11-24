# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** f759258 · **Base:** a1b2f2d · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `tests/test_todos_count.py::test_count_ignores_query_parameters` | `src/todo_api/todos/router.py:40-42`, `src/todo_api/todos/repository.py:38-44` | The test creates three todos and asserts `200`, `Content-Type` starting with `application/json`, and the body `{"count": 3}` exactly. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos_is_zero`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes`, `tests/test_todos_count.py::test_patch_count_invalid_body_stays_422`; existing endpoints: `tests/test_todos_api.py`, `tests/test_todos_title_patch.py` (unchanged since base) | `src/todo_api/todos/router.py:40-42` (new GET only); `router.py:56-83` (PATCH/DELETE `/{todo_id}`, unchanged, `parse_id("count")` gives `None` and the route raises `_not_found()`) | The tests assert `{"count": 0}` with an int type, and `404` with the exact `todo_not_found` body for `PATCH {"done": true}` and for `DELETE`. "Existing endpoints do not change": the diff touches no existing handler, and the spec 001/002 suites stay green in `devbox run ci`. |

## Non-goals

There is no filtering or paging: the query parameters are ignored, and `test_count_ignores_query_parameters` asserts this. No other endpoint changed. No gitops, configuration or schema change: `SCHEMA_SQL` is untouched and there is no migration. The build changed no template-owned files. ✔

## Deviations from the plan

None. Every changed source file (`repository.py`, `router.py`, `README.md`) is in t1's `files`, and the new test file is the testers' file, as the plan describes. t1 is `done: true`. The spec, plan and design files are spec-process documents.

## Contract

Matches `design.md`. `count_todos(conn) -> int` runs `SELECT count(*) FROM todos` and raises `RuntimeError` when there is no row. The `GET /count` handler returns `JSONResponse({"count": n})` through `db.run`, which gives the existing `503 unavailable` path. The `422` on an invalid PATCH body is kept, as the design states. ✔

## Mutation check (report only)

2 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

2 of 2 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
