# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 421e8cd · **Base:** 12cb290 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos via `POST /todos`, asserts `200`, `Content-Type` starting with `application/json`, and the parsed body `== {"count": 3}`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57`, `src/todo_api/todos/router.py:73`, `src/todo_api/todos/validation.py:67` | Empty database (autouse `_fresh_database` drops the table) gives `200` and `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both asserted `404` with the exact existing `todo_not_found` body; only a GET route was added, and `parse_id("count")` returns `None`, so the id handlers answer `_not_found()`. "Existing endpoints do not change": the diff leaves every existing handler untouched (`router.py` gains lines 40-44 only) and the pre-existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) are unchanged and green in `devbox run ci`. |

## Non-goals

No filtering, paging, or change to other endpoints; no schema, configuration or gitops change; no template-owned layout touched. ✔

## Deviations from the plan

- `tests/unit/test_count_todos.py` is in no task's `files`: a unit test for `repository.count_todos` (mocked connection); acceptable, internal tests need no task entry.
- `docs/specs/900-.../{spec,plan,design}.md` changed by the pipeline (status `building`, plan `done: true`); acceptable.
- Task t1 is `done: true`; no task is open.

## Contract

Matches `design.md`: `GET /todos/count` returns `JSONResponse({"count": n})` from `SELECT count(*) FROM todos` run through `db.run` (so the existing `503 unavailable` path applies); PATCH/DELETE `/todos/count` fall through to the id routes unchanged. ✔

## Mutation check (report only)

2 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

2 of 2 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
