# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** cd56c2c · **Base:** af6912a · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-41` | creates three todos, asserts `200`, `Content-Type` starting `application/json`, body `== {"count": 3}` and that `count` is an `int` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos_is_zero`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id` | `src/todo_api/todos/router.py:40-43`; unchanged `router.py:57-62`, `router.py:73-77` (`parse_id("count")` returns `None` → `_not_found()`, `router.py:30-31`) | asserts `200 {"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` answer `404` with the full `todo_not_found` body matching `errors.py:16`. "Existing endpoints do not change": the diff adds lines only; `patch_todo`, `delete_todo`, `list_todos`, `create_todo` and `validation.py` are untouched, and the existing suite passed unchanged (`cplat quiet ci` green) |

## Non-goals

No filtering, paging or change to the other endpoints; no gitops, configuration, schema or migration change (`SCHEMA_SQL` untouched). No template-owned layout change. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`; acceptable, the plan states the acceptance tests are written by the testers in a new file before coding.
- `docs/specs/900-.../spec.md` status/changelog update (`approved` → `building`); acceptable, pipeline bookkeeping.
- Task t1 is `done: true`; all its files (`repository.py`, `router.py`, `README.md`) changed as planned.

## Contract

Matches `design.md`: `GET /todos/count` → `200 {"count": <int>}` via one `SELECT count(*) FROM todos`; the handler goes through `db.run`, so the existing `DatabaseUnavailable` → `503` mapping applies (not covered by an acceptance test, not a criterion). The handler is named `count_todos_route` rather than the pseudocode's `count_todos`, avoiding a name clash; acceptable. ✔

## Mutation check (report only)

3 of 4 mutants of the changed code were caught by the acceptance tests (75 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/todo_api/todos/repository.py:41 0 → 1`
