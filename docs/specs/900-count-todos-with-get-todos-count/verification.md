# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 6a076f0 · **Base:** b6b547c · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/repository.py:38` | Creates three todos (each asserted 201), then asserts `200`, `content-type` starting with `application/json` and body exactly `{"count": 3}`. Count comes from `SELECT count(*) FROM todos` (`repository.py:39`), not from loading the list. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_zero_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:51` (GET only), id routes unchanged at `router.py:57` and `router.py:73` | Empty database (autouse `_fresh_database` drops the table per test): `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` each assert `404` with the full `todo_not_found` body, the same one an unknown id gets (`_not_found`, `router.py:30`). The shadow test first asserts GET is 200, so it could not pass before the route existed. "Existing endpoints do not change": no diff to existing handlers, `parse_id` or `_not_found`; existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) pass in `ci`. |

## Non-goals

No filtering, paging or query parameters on `/count`. No changes to other endpoints (the diff to `router.py` only adds lines 51-54). No schema, configuration or gitops change: `SCHEMA_SQL` untouched, no config or deploy files in the diff. No template-owned files (Dockerfile, CI workflow, `devbox.json`, `CLAUDE.md`) changed. ✔

## Deviations from the plan

- None in code: the only source files changed are `src/todo_api/todos/repository.py` and `src/todo_api/todos/router.py`, both in t1's `files`. `tests/test_todos_count.py` is the acceptance-test RED commit (58058e3), and the `docs/specs/900-*` files are the spec/plan/design themselves; both acceptable.
- t1 is `done: true`.
- Implementation follows the plan's notes: `count_todos(conn) -> int` raises `RuntimeError` on no row (`repository.py:41-42`); route declared before `@router.patch("/{todo_id}")`; no PATCH/DELETE handlers for `/count`.

## Contract

Matches `design.md`: `GET /todos/count` returns `200`, `application/json`, body with exactly one integer key `count` (`int(row[0])`, `repository.py:43`). The `503 unavailable` case goes through the existing `DatabaseUnavailable` handler via `db.run` (same path as `GET /todos`); no acceptance criterion asks for it and no test exercises it for this route, which is acceptable since it is inherited behaviour. `PATCH`/`DELETE /todos/count` give `404 todo_not_found` as specified. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
