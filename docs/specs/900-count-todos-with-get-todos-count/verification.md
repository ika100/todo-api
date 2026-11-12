# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** c680357 · **Base:** af5ff92 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos, asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}`. A single `SELECT count(*) FROM todos`, cast to `int`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (static `/count` declared before `/{todo_id}`); unchanged `patch_todo` `router.py:57-70`, `delete_todo` `router.py:73-84` | Empty DB (autouse fresh-database fixture, `tests/conftest.py:75`) gives `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` with the exact `todo_not_found` body, and the existing todo survives. "Existing endpoints do not change": the diff touches no other route, and `tests/test_todos_api.py` / `tests/test_todos_title_patch.py` are unchanged and green (Phase 3 `ci`). |

## Non-goals

No filtering, paging or query-parameter handling was added. No other endpoint changed. No schema, configuration or gitops change (`SCHEMA_SQL`, `pyproject.toml`, `Dockerfile`, CI and env docs untouched). No template-owned layout change. ✔

## Deviations from the plan

None. Every changed source file (`repository.py`, `router.py`, `README.md`) is in t1's `files`; `tests/test_todos_count.py` is the new acceptance test file the plan names; the spec docs belong to the spec. t1 is `done: true`. The repository function adds a `RuntimeError` guard when no row comes back, a defensive branch that never fires for `count(*)`; this is acceptable.

## Contract

Matches `design.md`: `200` `application/json` `{"count": <int>}` with no other fields; the 503 path goes through the unchanged `db.run`; `PATCH`/`DELETE /todos/count` give `404 todo_not_found`. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
