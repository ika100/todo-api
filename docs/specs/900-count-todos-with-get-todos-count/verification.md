# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 229f83a · **Base:** 50b9ce1 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-43` | Creates three todos (each asserted `201`), then asserts `200`, a `content-type` starting with `application/json` and the body exactly `{"count": 3}`. The count comes from `SELECT count(*) FROM todos` through `db.run`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_count_does_not_shadow_patch`, `::test_count_does_not_shadow_delete`, `::test_count_route_exists_alongside_unchanged_list` | `src/todo_api/todos/router.py:40` (static `GET /count` only), `src/todo_api/todos/router.py:57-60` and `:73-75` (unchanged `patch_todo`/`delete_todo`; `parse_id("count")` at `src/todo_api/todos/validation.py:67-72` returns `None`, so `_not_found()` is raised) | The empty case asserts `200` and `{"count": 0}`. The autouse `_fresh_database` fixture at `tests/conftest.py:74-81` drops the table, so the database is empty. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` with the exact `todo_not_found` body. For "existing endpoints do not change": the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) and `tests/conftest.py` are unmodified since base and pass (164 tests green). |

## Non-goals

There is no filtering, paging or query-parameter handling: the handler at `src/todo_api/todos/router.py:41-43` reads neither the query nor the body. The other endpoints are unchanged; the diff only adds lines to `router.py` and `repository.py`. There is no schema change (`SCHEMA_SQL` is untouched), and no gitops or configuration change. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. This is acceptable: the plan says the acceptance tests are written by the testers in a new file before coding. It is unchanged since the red commit `bd1ac18`.
- Spec docs (`spec.md` status/changelog, `plan.md`, `design.md`) are workflow artifacts. Acceptable.
- Task t1 is marked `done: true`. No other tasks.

## Contract

The build matches `design.md`:
- `GET /todos/count` returns `200` and `{"count": <int>}` as `JSONResponse`, which sets `application/json`. `count` is the only key.
- `503 unavailable` is inherited through `db.run`, the same path `GET /todos` uses. No test targets the 503 path for this route, but the contract states it as inherited behaviour and it is not an acceptance criterion.
- `PATCH`/`DELETE /todos/count` return `404 todo_not_found`.
- The README line and the spec link were added as planned. ✔
