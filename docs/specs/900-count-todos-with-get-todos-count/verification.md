# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** d3b4118 · **Base:** 7f7a378 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos, then asserts `200`, `content-type` starting with `application/json`, and body `== {"count": 3}` (exact, no extra fields). The count comes from `SELECT count(*) FROM todos`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos_is_zero`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id` | `src/todo_api/todos/router.py:40` (GET only); `router.py:57-60`, `router.py:73-75` unchanged (`parse_id("count")` gives `None`, which leads to `_not_found`) | Asserts `200 {"count": 0}` with no todos. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` each assert `404` and the exact `todo_not_found` body. "Existing endpoints do not change": the diff touches no other handler, and the existing `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass (green CI). |

## Non-goals

The diff adds no filtering, paging or query parameters. No other endpoint changed. No gitops, configuration or schema change was made, and no template-owned files were touched. ✔

## Deviations from the plan

None. Every changed source file is in t1's `files`. t1 is `done: true`. The only other changes are the new acceptance test file and the spec docs.

## Contract

Matches `design.md`. The route is `GET /todos/count` and returns `JSONResponse({"count": n})`. `n` is a Python `int`, so the body has no other fields. `503` comes from the existing `DatabaseUnavailable` handler through `db.run`, the same path as `GET /todos`. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
