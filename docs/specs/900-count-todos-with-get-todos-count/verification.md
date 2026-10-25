# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** e1bb05d · **Base:** 63afe7d · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `tests/test_todos_count.py::test_count_includes_done_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Asserts status `200`, `content-type` starts with `application/json`, and body `== {"count": 3}`. Exact equality means exactly one key and an integer value (`3 != "3"`). `count_todos` runs `SELECT count(*) FROM todos` and returns `int(row[0])`. The handler wraps it in `JSONResponse({"count": n})`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `::test_patch_count_is_not_found`, `::test_delete_count_is_not_found`; existing endpoints: unchanged `tests/test_todos_api.py`, `tests/test_todos_title_patch.py` | `src/todo_api/todos/router.py:40` (GET only); `router.py:57-62` and `router.py:73-77` (unchanged id routes, `parse_id("count")` gives `None`, then `_not_found()`) | Empty gives `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both give `404` with the exact `todo_not_found` body. The diff only adds lines to `router.py` and `repository.py`. The existing handlers, `parse_id` and the existing test files are untouched (`git diff --stat` on base shows no change to them). They pass under `devbox run ci`. |

## Non-goals

No filtering, paging, schema change (`SCHEMA_SQL` untouched), configuration change or gitops change. The count includes done todos (`test_count_includes_done_todos`), so there is no filtering. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: the plan assigns acceptance tests to the testers in a new file (red commit 96c1d44). The file is unchanged since that commit (`git diff 96c1d44..HEAD -- tests/` is empty).
- Spec docs (`spec.md` status/changelog, `design.md`, `plan.md`). Acceptable: pipeline bookkeeping.
- t1 is `done: true`. No other tasks.

## Contract

Matches `design.md`. The signatures `count_todos(conn) -> int` and `GET /count -> JSONResponse({"count": n})` match. The route is GET only, with no `PATCH`/`DELETE` on `/count` and no `"count"` special case in `parse_id`. The 503 path is inherited from `Database.run`, as the design states. No test covers it, and no criterion requires one. The README line and the spec 900 link were added as the plan describes. ✔
