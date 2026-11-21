# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 23f12b0 · **Base:** f1bfdfd · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates 3 todos, asserts `200`, `content-type` starts with `application/json`, parsed body `== {"count": 3}` (exactly one key) |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (GET only on `/count`), `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` (`parse_id("count")` is `None`, so `todo_not_found`) | empty DB asserts `200` + `{"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` with the full `todo_not_found` body (`errors.py:16` message matches); the todo survives (`GET /todos` length 1). "Existing endpoints do not change": the router diff only adds the new handler, and the existing suite passes unchanged (`devbox run ci` green) |

## Non-goals

No filtering, paging or query parameters on `/todos/count`; no other endpoint is modified (diff to `router.py` is additive only). No schema, configuration or gitops change: the diff touches only `repository.py`, `router.py`, the test file and the spec docs. ✔

## Deviations from the plan

- None. The changed source files (`src/todo_api/todos/repository.py`, `src/todo_api/todos/router.py`) are exactly t1's `files`; `tests/test_todos_count.py` is the acceptance-test commit; t1 is `done: true`. The `spec.md` status/changelog change (`building`) is pipeline bookkeeping; acceptable.

## Contract

Matches `design.md`: one `SELECT count(*) FROM todos` (`repository.py:38-44`, `RuntimeError` on no row as planned), `GET /todos/count` returns `JSONResponse({"count": n})` through `db.run` (so the existing `DatabaseUnavailable` to `503` path applies), declared above the `/{todo_id}` routes, no `PATCH`/`DELETE` handler on `/count`. ✔

## Mutation check (report only)

2 of 4 mutants tested in 90 s (time budget of 90 s, `--budget`); the score covers the tested ones.

2 of 2 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
