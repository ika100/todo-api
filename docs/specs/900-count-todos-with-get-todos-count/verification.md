# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 8681075 · **Base:** 783c55d · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/repository.py:50` | Creates 3 todos through `POST /todos`, asserts `200`, `content-type` starts with `application/json`, and exact body equality `{"count": 3}` (no other keys). The count comes from a single `SELECT count(*) FROM todos` (`repository.py:51`), returned as `int` (`repository.py:55`). |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_count_does_not_shadow_patch`, `::test_count_does_not_shadow_delete` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` | Empty DB gives `200 {"count": 0}` with JSON content type. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both give `404` with the exact body `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. The route is GET-only, so PATCH and DELETE still reach the unchanged id handlers. `parse_id("count")` returns `None` there, which leads to `_not_found()` (`router.py:31`). "Existing endpoints do not change": the diff does not touch `list_todos`, `create_todo`, `patch_todo` or `delete_todo`. `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are unmodified and pass (`devbox run ci` green). |

## Non-goals

There is no filtering or paging: the handler reads no query parameters (`router.py:52-54`). No other endpoint changed. No gitops, configuration, schema or migration change: `SCHEMA_SQL` is untouched and no env var was added. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: the plan says the testers write the AC-900 tests in a new test file before coding (red commit `06b3176`). Coding commit `652c357` did not touch it.
- The spec docs (`spec.md` status/changelog, `plan.md`, `design.md`) changed. Acceptable: these are pipeline bookkeeping.
- t1 is `done: true`. No tasks are open.

## Contract

Matches `design.md`:
- `GET /todos/count` → `200 {"count": <int>}` as `JSONResponse`.
- The route is declared after `list_todos`/`create_todo` and before the `/{todo_id}` routes.
- No `GET /{todo_id}` route was added.
- 503 goes through the shared `Database.run` path (`router.py:53`). No AC-900 test covers 503, and the spec does not require one.
- README line and spec 900 link added as the plan specifies. ✔
