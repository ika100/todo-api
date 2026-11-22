# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 5c271df · **Base:** 607e847 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos; asserts `200`, `content-type` starts with `application/json`, decoded body `== {"count": 3}`, and the count is an `int`. The count comes from one `SELECT count(*)` through `db.run`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes`; existing `tests/test_todos_api.py`, `tests/test_todos_title_patch.py` (unchanged, green in `devbox run ci`) | `src/todo_api/todos/router.py:40` (static `GET /count` only); `patch_todo`/`delete_todo` unchanged, `parse_id("count")` gives `None` → 404 (`src/todo_api/todos/validation.py:67`) | Empty table: `200 {"count": 0}`, int. `PATCH /todos/count {"done": true}` and `DELETE /todos/count`: `404` with the exact `todo_not_found` body. The test first asserts `GET /todos/count == 200`, so it cannot pass without the route. "Existing endpoints do not change" is covered by the unchanged spec 001/002 suites. |

## Non-goals

No filtering, paging or change to other endpoints: the diff touches only the new handler and the new repository function. No gitops, configuration or schema change: `SCHEMA_SQL`, `pyproject.toml`, `Dockerfile` and CI are untouched. No template-owned layout change. ✔

## Deviations from the plan

- `tests/conftest.py` (commit 5c271df) is outside every task's `files`. The plan says the acceptance tests use "the existing `tests/conftest.py` harness". The `client` fixture now sets the global `todo_api.db.OP_DEADLINE_S` to at least 10 s for every real-Postgres test that uses `client`, so the spec 001, 002 and 900 suites no longer run the production 1 s deadline. Checks: no assertion changed; no deadline test (AC-001.17, AC-001.18, AC-002.13) uses `client` (they use `make_app`/`container_url`); unit tests still patch the deadline themselves; the value is restored in `finally`. No AC-900 criterion states a latency, so no criterion is weakened. **Not acceptable as an unrecorded change:** it changes the shared, frozen harness of three specs to stop load flakes, it is not in the plan, and `cplat spec test-diff` does not see it. Either record it as its own change with a reason (a plan amendment or a separate `fix/`/`chore/` PR), or have the orchestrator explicitly accept it in this PR.
- `README.md`: in t1 `files`, the change matches the plan. ✔
- t1 `done: true`. ✔

## Contract

Matches `design.md`: `GET /todos/count` returns `200 application/json {"count": <int>}` with a single key, through `db.run`, so the existing `503 unavailable` mapping applies. No PATCH/DELETE handler was added for `/count`. No `ux.md` (API only). ✔
