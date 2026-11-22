# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 707e5f1 · **Base:** 1b74ae1 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos (each asserted 201), asserts `200`, media type `application/json`, body `== {"count": 3}`; count comes from `SELECT count(*)` via `db.run` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57`, `src/todo_api/todos/router.py:73` | asserts `200` `{"count": 0}` on a fresh DB (autouse `_fresh_database` drop); `PATCH /todos/count` `{"done": true}` and `DELETE /todos/count` each asserted `404` with the exact `todo_not_found` body. Static `GET /count` has no `GET /{todo_id}` to shadow; `patch_todo`/`delete_todo` unchanged, `parse_id("count")` gives `None` and the 404. "Existing endpoints do not change": the diff touches no other handler and the existing suite passes unchanged (`cplat spec test-diff`: no acceptance test changed; `devbox run ci` green) |

## Non-goals

No filtering, paging, or change to other endpoints; no gitops, configuration or schema change (no migration, no config touched). No template-owned layout changes. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`; acceptable, it is the acceptance test file written from the criteria before the build.
- Spec docs (`spec.md` status/changelog, `plan.md`, `design.md`) changed; acceptable, pipeline bookkeeping.
- Task t1 is `done: true`. No other deviations.

## Contract

Matches `design.md`: `GET /todos/count` → `200` `{"count": <int>}` as `JSONResponse`; goes through `app.state.db.run`, so the existing 503 `unavailable` handling applies; `PATCH`/`DELETE /todos/count` → existing 404 `todo_not_found`. ✔

## Mutation check (report only)

2 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

2 of 2 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
