# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 7cb0f40 · **Base:** b117fde · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates 3 todos, asserts `200`, `Content-Type` starts with `application/json`, body `== {"count": 3}`, count is an int and not a bool |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id`; unchanged `tests/test_todos_api.py`, `tests/test_todos_title_patch.py` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:56-61`, `src/todo_api/todos/router.py:72-76` | empty DB (autouse `_fresh_database` drops the table) gives `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` give `404` with the exact `todo_not_found` body (same constant as `tests/test_todos_api.py:17`, source `src/todo_api/errors.py:16`), and the existing todo is left untouched. The existing endpoints are unchanged: the PATCH/DELETE handlers have no diff, the existing test files have no diff, and `devbox run ci` is green |

## Non-goals

No filtering, paging, or change to other endpoints. No gitops, config, or schema change (`SCHEMA_SQL` is untouched; the only new SQL is a static `SELECT count(*) FROM todos`). No template-owned layout change. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: the plan says testers write the acceptance tests in a new file before coding.
- `docs/specs/900-.../{spec,plan,design}.md` changed. Acceptable: these are spec-lifecycle documents (status `building`, plan, design).
- Task t1 is `done: true`. All planned files changed as described.

## Contract

Matches `design.md`: `GET` only, `{"count": <int>}` via `app.state.db.run` (inherits the existing deadline and `503` mapping), and no special case for `count` in `patch_todo`/`delete_todo`. The handler and query match the design sketch. ✔

## Mutation check (report only)

3 of 4 mutants of the changed code were caught by the acceptance tests (75 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/todo_api/todos/repository.py:41 0 → 1`
