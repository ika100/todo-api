# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 9cfa5b0 · **Base:** c63f332 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos`, `::test_count_follows_creates_and_deletes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | asserts `200`, `content-type` starting with `application/json`, body exactly `{"count": 3}` after three creates |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_count_with_never_used_database`, `::test_count_does_not_shadow_id_routes`, `::test_other_endpoints_unchanged` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` | asserts `{"count": 0}` with `200`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` answer `404` with the full `todo_not_found` body; list and patch of a real id behave as before. No `/count` handler for PATCH/DELETE was added, so `parse_id("count")` on the existing id routes yields the 404 |

## Non-goals

No filtering, paging, gitops, configuration or schema change. The other handlers are unchanged in the diff (only lines 40-43 added to `router.py`). ✔

## Deviations from the plan

- `tests/unit/test_db_internals.py` changed but is in no task's `files`, and the plan says "no other test file is edited": two added unit tests for `repository.count_todos` (int conversion, `RuntimeError` on no row); no existing test changed. Acceptable: additive, covers the `RuntimeError` branch the plan asks for.
- `tests/test_todos_count.py` is in no task's `files`: it is the acceptance test file written from the criteria before the build (red commit f5fd7d5, unchanged since). Acceptable.

## Contract

Matches `design.md`: `GET /todos/count` returns `JSONResponse({"count": n})` with `n` from `SELECT count(*) FROM todos` through `app.state.db.run` (same `503 unavailable` path as the other routes); signatures as specified. ✔
