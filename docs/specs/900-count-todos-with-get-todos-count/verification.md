# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 9c78987 · **Base:** 2db7d8e · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos (each asserted 201), asserts `200`, `content-type` starts with `application/json`, decoded body `== {"count": 3}` and `count` is an `int`. Handler returns `JSONResponse({"count": n})` from one `SELECT count(*) FROM todos` through `db.run`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_patch_count_is_not_found`, `::test_delete_count_is_not_found` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` | Empty DB: `200`, `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` and the full body `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, the same body `_not_found()` (`router.py:30`, `errors.py:16`) yields for any unknown id; each first asserts `GET /todos/count` is `200`, so the test proves non-shadowing with the route present. "Existing endpoints do not change": `patch_todo`/`delete_todo`/`list_todos`/`create_todo` are untouched in the diff, and the unchanged existing suites `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pass (`devbox run ci` green). |

## Non-goals

No filtering, paging or change to other endpoints: the diff only adds `count_todos` in `repository.py` and the `GET /count` handler in `router.py`. No gitops, configuration, schema (`SCHEMA_SQL` untouched), `pyproject.toml` or `Dockerfile` change. No template-owned layout changes. ✔

## Deviations from the plan

- None. Changed source files (`repository.py`, `router.py`, `README.md`) are all in t1's `files`; `tests/test_todos_count.py` is the testers' acceptance file the plan names; the spec/plan/design docs are pipeline artifacts. t1 is `done: true`. No acceptance test changed after the reviewed RED commit `f0dfa72`.

## Contract

Matches `design.md`: `GET /todos/count` → `200 application/json {"count": <int>=0>}` via `db.run` (so `503 unavailable` mapping is inherited, as for `GET /todos`); `PATCH`/`DELETE /todos/count` → `404 todo_not_found` via the unchanged id routes; implementation is identical to the design pseudocode. ✔

## Mutation check (report only)

4 of 5 mutants of the changed code were caught by the acceptance tests (80 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/todo_api/todos/repository.py:41 0 → 1`
