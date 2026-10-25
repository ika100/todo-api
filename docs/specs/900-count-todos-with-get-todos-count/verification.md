# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 7a4abfe · **Base:** 3e62614 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos via `POST /todos` (asserts 201 each), then asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` and that `count` is an `int` (not `bool`). Count comes from `SELECT count(*) FROM todos`, cast with `int()`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_patch_count_is_not_found`, `::test_delete_count_is_not_found` | `src/todo_api/todos/router.py:40` (count route, declared before the id routes at `:57` and `:73`); unchanged `patch_todo`/`delete_todo` reject `"count"` via `parse_id` (`src/todo_api/todos/validation.py:67`) and raise `todo_not_found` (`router.py:31`) | Empty DB gives `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` with the exact `todo_not_found` body. "Existing endpoints do not change": the diff to `router.py` and `repository.py` is additive only (no existing line modified), and the existing suite passes (163 passed in `devbox run ci`). |

The acceptance tests in `tests/test_todos_count.py` were not modified after the red commit `952773b` (`git diff 952773b..HEAD -- tests` is empty).

## Non-goals

No filtering, paging, or changes to other endpoints; no gitops, configuration or schema change. The diff touches only `repository.py`, `router.py`, the new test file and the spec docs. ✔

## Deviations from the plan

- None. Code files changed are exactly t1's `files` (`src/todo_api/todos/repository.py`, `src/todo_api/todos/router.py`); `tests/test_todos_count.py` is the acceptance test file from the red phase. t1 is `done: true`.
- Minor: `count_todos` adds a defensive `RuntimeError` when `fetchone()` returns `None` (`repository.py:41-42`); unreachable for `count(*)`, and needed for typing. Acceptable.

## Contract

Matches `design.md`: `GET /todos/count` → `200 application/json {"count": <int>}` with `count` as the only key; database failures go through `Database.run` (existing `503 unavailable` path); route declared after `list_todos` and before the `/{todo_id}` routes; `PATCH`/`DELETE /todos/count` → `404 todo_not_found` without special-casing. ✔
