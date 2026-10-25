# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 4d653fa · **Base:** 24b57d5 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos, then asserts `200`, a `content-type` starting with `application/json`, and the exact body `{"count": 3}`. The count comes from `SELECT count(*) FROM todos` through `Database.run`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_patch_count_is_not_found`, `::test_delete_count_is_not_found`, `::test_count_route_exists_and_does_not_break_list` | `src/todo_api/todos/router.py:40` (static GET only); unchanged `router.py:57-62` and `router.py:73-77` (`parse_id("count")` is `None`, so `_not_found()` runs) | Empty table gives `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both return `404` with the exact `todo_not_found` body. The diff leaves the other handlers alone, and the existing suites for specs 001/002 still pass (164 passed), which covers "existing endpoints do not change". |

## Non-goals

There is no filtering, paging or schema change: `SCHEMA_SQL` is untouched, and there is no migration, gitops change or new environment variable. The only change to other endpoints is that a new route was registered. ✔

## Deviations from the plan

- The changes in `tests/test_todos_count.py` and `docs/specs/900-.../{design,plan,spec}.md` are outside t1's `files`. This is acceptable: these are the acceptance tests written red first, plus pipeline spec, plan and status bookkeeping.
- t1 is `done: true`. There are no other tasks.

## Contract

The code matches `design.md`. `GET /todos/count` returns `200 {"count": <int>}` as `application/json` with exactly one key. A timeout returns `503` through the shared `Database.run` path. The route is registered after `list_todos` and above the `/{todo_id}` routes. `PATCH` and `DELETE /todos/count` return `404 todo_not_found`. One minor point: no test covers the `503` path for this endpoint. That path is shared, and no acceptance criterion requires it, so it does not affect the verdict. ✔
