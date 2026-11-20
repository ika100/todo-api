# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** c3cb880 · **Base:** 56ba09a · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates 3 todos (one marked done, so the count is not filtered), asserts `200`, `Content-Type` starting with `application/json`, body exactly `{"count": 3}` and `count` a JSON int |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`; id routes unchanged at `src/todo_api/todos/router.py:57`, `:73` | empty DB gives `200 {"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` assert `404` with the full `todo_not_found` body, and equal the response for unknown ids (`999999`, a UUID); "existing endpoints do not change" rests on the unchanged existing suite (`tests/test_todos_api.py`, green in `devbox run ci`) and on the diff, which touches no existing handler |

## Non-goals

No filtering, paging, or change to other endpoints; no gitops, configuration or schema change. No template-owned layout touched. ✔

## Deviations from the plan

None. Every changed source file is in t1's `files`; t1 is `done: true`; the remaining touched files are the spec's own docs and the acceptance test.

## Contract

Matches `design.md`: `200 {"count": n}` as a JSON int, computed by `SELECT count(*) FROM todos`; `PATCH`/`DELETE` on `/todos/count` give `404 todo_not_found`; `503` comes from the existing `DatabaseUnavailable` handler via `db.run` (not separately tested, no criterion asks for it). ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
