# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** e22e34a · **Base:** 18cc1da · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/router.py:57`, `src/todo_api/todos/router.py:73` | empty table (autouse `_fresh_database` drops it) gives `200 {"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` assert `404` with the exact `todo_not_found` body (same as `MSG_TODO_NOT_FOUND`, `src/todo_api/errors.py:16`); `parse_id("count")` is `None`, so `_not_found()` answers. "Existing endpoints do not change": `patch_todo`/`delete_todo`/`list_todos`/`create_todo` untouched in the diff, `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` unchanged and green in `devbox run ci` |

## Non-goals

No filtering, paging, or change to other endpoints; no gitops, configuration or schema change (`SCHEMA_SQL` untouched, no migration, no env var). No template-owned layout touched. ✔

## Deviations from the plan

- `docs/specs/900-.../spec.md`, `plan.md`, `design.md` changed outside task `files`: spec status `approved` -> `building` with changelog line, plan/design are the planning artifacts; acceptable (pipeline bookkeeping).
- `tests/test_todos_count.py` is outside task `files`: the plan assigns acceptance tests to the testers before coding; acceptable.
- Task t1 has `done: true`. No other deviation.

## Contract

Matches `design.md`: `GET /todos/count` returns `JSONResponse({"count": n})` from one `SELECT count(*) FROM todos` through `db.run` (503/500 via existing handlers); route declared above the id routes; PATCH/DELETE `/todos/count` keep the `404 todo_not_found` body. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
