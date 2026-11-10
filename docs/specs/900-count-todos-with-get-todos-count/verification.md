# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 2a68f0b · **Base:** 4a211a5 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `tests/test_todos_count.py::test_count_includes_done_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Three todos via `POST /todos`, then asserts `200`, `content-type` starts with `application/json`, body equals `{"count": 3}` (decoded), and `count` is an `int`. A second test checks that done todos are counted too. `SELECT count(*) FROM todos` goes through `Database.run`, as the design says. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id`, `::test_count_ignores_query_parameters` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:57-62` and `:73-77` (existing `parse_id` → `_not_found`, unchanged) | Empty table returns `200 {"count": 0}` with an int. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` return `404` with the exact `todo_not_found` body, and DELETE leaves the todo in place. "Existing endpoints do not change": the diff only adds lines to `router.py`/`repository.py`, no existing handler or test file is touched, and the existing suites (`test_todos_api.py`, `test_todos_title_patch.py`) pass in `cplat quiet ci`. |

## Non-goals

No filtering or paging: query parameters are ignored (`test_count_ignores_query_parameters`). No other endpoint changed. `SCHEMA_SQL` is unchanged, and there is no migration, config, env-var or gitops change. Template-owned layout is not touched. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: the plan says testers write the acceptance tests in this file before coding, and it has not changed since the red commit `34dffef` (`git diff 34dffef..HEAD -- tests/` is empty).
- `docs/specs/900-.../{spec,plan,design}.md` changed outside task files. Acceptable: these are the pipeline's own status, plan and design edits. `design.md` was reformatted in `f0ec11d` (code block layout only, no change to the contract).
- Task t1 is `done: true`. Nothing is left undone.

## Contract

Matches `design.md`. The route is `GET`-only and declared above the `/{todo_id}` routes (`router.py:40`). The body is exactly `{"count": <int>}`. `PATCH`/`DELETE` on `/todos/count` reach the existing handlers without database access (`parse_id` returns `None` before `db.run`). There is no special case for `"count"` in `patch_todo`, `delete_todo` or `parse_id`. The `503` path is the unchanged `Database.run` behaviour (not covered by an acceptance test, and no criterion requires it). ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
