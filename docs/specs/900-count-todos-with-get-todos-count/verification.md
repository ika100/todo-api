# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 007be45 · **Base:** 53a45ce · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | The test creates three todos and asserts `200`, a `content-type` starting with `application/json`, and the parsed body `== {"count": 3}`. The count comes from `SELECT count(*) FROM todos`, as design.md says. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_zero_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:57-62` and `:73-77` (unchanged id handlers turn `count` into `todo_not_found`) | Covers the empty-table case: `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` each return `404` with the exact `todo_not_found` body. The test then checks that the todo is still listed by `GET /todos` and that the count reads 1. The rest of the router diff is untouched, and the existing suite passes (`devbox run ci` green). |

## Non-goals

There is no filtering or paging, and no other endpoint changed: the diff only adds lines to `router.py` and `repository.py`. There are no gitops, configuration or schema changes, and no template-owned layout changes. ✔

## Deviations from the plan

None. Every changed source file is in t1's `files`. The other changed files are the spec documents and the acceptance test from the red commit. t1 is `done: true`.

## Contract

The code matches `design.md`: `GET /todos/count` answers `200 {"count": int}` with `application/json`. The route is registered GET-only, before the `/{todo_id}` routes. `count_todos(conn) -> int` uses `conn.execute` as planned. The repository also raises `RuntimeError` if the query returns no row. That is a defensive extra for mypy and does not change the contract, so it is acceptable. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
