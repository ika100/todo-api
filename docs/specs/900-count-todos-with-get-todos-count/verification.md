# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 2b1ae43 · **Base:** 9fe5a58 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos_returns_count`, `tests/test_todos_count.py::test_count_counts_done_and_open_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-44` | The first test creates exactly three todos on a fresh database (autouse `_fresh_database` in `tests/conftest.py`) and asserts `200`, `content-type` starting with `application/json`, and body `== {"count": 3}`. Equality on the whole body also proves `count` is the only key. The second test shows done todos are counted too (design contract). The count comes from one `SELECT count(*) FROM todos` (repository.py:40), as design.md requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty_is_zero`, `::test_patch_count_is_todo_not_found`, `::test_delete_count_is_todo_not_found` | `src/todo_api/todos/router.py:40` (static GET route declared before `/{todo_id}` at :57 and :73); unchanged `patch_todo` router.py:57-62, `delete_todo` router.py:73-77 | Empty database gives `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` and the exact `todo_not_found` body (`"This todo no longer exists"`). "Existing endpoints do not change": the diff touches no existing handler, no existing test file changed (`git diff 9fe5a58..HEAD --stat` shows only `tests/test_todos_count.py` under tests), and the existing suites pass in `devbox run ci`. |

## Non-goals

No filtering, paging, or query parameters on the count endpoint. No changes to other endpoints, schema (`SCHEMA_SQL` untouched), configuration, or gitops. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: these are the acceptance tests from the red commit 7750269, and the plan says testers write them before t1. They have not changed since then (no diff 7750269..HEAD).
- Spec docs (`spec.md` status `building`, `plan.md`, `design.md`) changed through the pipeline's own commits. Acceptable.
- t1 `done: true`. No unfinished tasks.

## Contract

Matches `design.md`. `GET /todos/count` returns `200 {"count": n}` as JSON (router.py:43). The repository function signature `count_todos(conn: AsyncConnection) -> int` matches, and it raises `RuntimeError` when no row comes back, as planned (repository.py:42-43). Database unavailability goes through `Database.run` (router.py:42) to the existing `503 unavailable` handler. PATCH and DELETE fall through to the unchanged id routes. ✔

Minor, not a criterion: no test covers the contract's `503` on `/todos/count`, or `405` for `POST`/`PUT /todos/count`. Both follow from existing shared machinery (`Database.run`, router method matching), not from new code.
