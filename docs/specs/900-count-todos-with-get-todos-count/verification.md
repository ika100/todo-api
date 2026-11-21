# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 198e03a · **Base:** 600ca15 · **Trace:** 2/2 criteria named by tests (`missing: []`)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:51-54`, `src/todo_api/todos/repository.py:38-41` | The test creates three todos on a fresh database (autouse `_fresh_database`, `tests/conftest.py:74`) and asserts `200`, `content-type` starting with `application/json`, and the decoded body `== {"count": 3}`. `JSONResponse` sends `application/json`. The count comes from `SELECT count(*) FROM todos`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes`; the existing suite `tests/test_todos_api.py` is unchanged and passes | `src/todo_api/todos/router.py:51-54` (GET only); `router.py:57-84` (`patch_todo`/`delete_todo` not changed, `parse_id("count")` gives `None`, so `_not_found()` runs) | Empty database: `200` and `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` each assert `404` with a body equal to `NOT_FOUND` (`todo_not_found`, "This todo no longer exists", `tests/test_todos_api.py:17`, matching `errors.py:16`). After these calls the existing todo is still present and the count is 1, so neither call reached a todo. "Existing endpoints do not change": the diff only adds code to the router, and the unchanged `tests/test_todos_api.py` suite is green. |

## Non-goals

- No filtering, paging or query parameters were added. `count_todos` takes no parameters, and the other endpoints' code is unchanged in the diff. ✔
- No gitops, configuration, schema or dependency change: `SCHEMA_SQL`, `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` are not touched. ✔
- No template-owned layout change. `README.md` gains only the planned API line and spec link. ✔

## Deviations from the plan

- None in code. Every changed source file and the README fall within t1's `files`, and t1 is `done: true`. The other changed files are the spec's own documents (`spec.md` status change to `building`, `plan.md`, `design.md`), which belong to the pipeline. This is acceptable.

## Contract

Matches `design.md`: `GET /todos/count` returns `200 {"count": <int>}` with no other fields and runs through `Database.run`, so the existing `503 unavailable` mapping applies. The contract's 503 behaviour is not part of any criterion and has no test of its own. No `PATCH` or `DELETE` handler was added on `/count`. The code is identical to the design sketch. ✔

## Observations (no effect on the verdict)

- `tests/test_todos_count.py:5` contains `from conftest import UNREACHABLE_URL  # noqa: F401`. The import is unused, so this is a real unused import, not a false positive. It has been there since the red commit `8cbed02`, so the coder did not add it, and it has no effect on any assertion. `SUPPRESSIONS` was reported as `none`. Cleaning it up is optional.
- The test for AC-900.1 checks `content-type` with `startswith("application/json")`. This is the same idiom as `tests/test_todos_api.py:22`. The header sent is exactly `application/json`, so the check is not weaker than the criterion.

## Mutation check (report only)

2 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

1 of 2 mutants of the changed code were caught by the acceptance tests (50 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/todo_api/todos/repository.py:41 0 → 1`
