# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 94a6940 · **Base:** 19f9403 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos (asserting 201 each), then asserts `200`, `Content-Type` media type `application/json`, and the exact body `{"count": 3}`. The count comes from `SELECT count(*) FROM todos` against a real Postgres (`tests/conftest.py:49`), not from stubs. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_patch_count_is_not_found`, `::test_delete_count_is_not_found`, `::test_count_route_does_not_break_existing_list` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` | Empty table gives exact `{"count": 0}` with 200. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both give 404 with the full `todo_not_found` error body (code and message). That works because only GET is registered for `/count`, so `parse_id("count")` returns `None` in the existing handlers. "Existing endpoints do not change": the diff does not touch `list_todos`, `create_todo`, `patch_todo`, `delete_todo` or `to_json`, and the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`, `tests/conftest.py`) are unchanged and pass (164 tests). |

## Non-goals

No filtering or paging: the handler reads no query parameters (`router.py:41-43`). The other endpoints did not change. No gitops, configuration, schema or migration change: `SCHEMA_SQL` is untouched and there is no diff in `pyproject.toml`, `Dockerfile`, CI or `docs/env-vars.md`. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: the plan says the testers write the acceptance tests in a new file before coding (red commit be564bf).
- `docs/specs/900-.../spec.md` (status set to `building`, changelog entry), `plan.md` and `design.md` are in no task's `files`. Acceptable: these are pipeline bookkeeping, not product code.
- Task t1 is `done: true`. None of its files is missing from the diff.

## Contract

Matches `design.md`: GET-only route at the literal path `/todos/count`. It returns `{"count": <int>}` with no other keys and goes through `Database.run`, so the existing 503 mapping applies. It adds no PATCH or DELETE handler, no GET `/{todo_id}` and no 405 handling. `count_todos(conn) -> int` raises `RuntimeError` when no row comes back, as the plan says. The README lists the endpoint and links to spec 900. ✔
