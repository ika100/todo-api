# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** a918393 · **Base:** ad346a0 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_with_three_todos` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/repository.py:38` | creates three todos; asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` and the value is an `int` |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_with_no_todos`, `::test_count_does_not_shadow_id_routes`, `::test_existing_endpoints_unchanged` | `src/todo_api/todos/router.py:51` (GET only; PATCH/DELETE fall through to the unchanged `/{todo_id}` handlers) | asserts `200 {"count": 0}` with no todos; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` answer `404` with the exact `todo_not_found` body; GET/POST/PATCH/DELETE on real ids behave as before |

## Non-goals

There is no filtering, no paging and no change to the other endpoints. `patch_todo`, `delete_todo` and `parse_id` are untouched. There is no gitops, config, schema or `SCHEMA_SQL` change, and no template-owned layout change. ✔

## Deviations from the plan

None. Every changed file (`README.md`, `repository.py`, `router.py`) is in t1's `files`. The new test file is the acceptance-test file the plan foresees. t1 is `done: true`. The route sits after `create_todo` and before `patch_todo`, as planned.

## Contract

Matches `design.md`: one `SELECT count(*) FROM todos` returned as an `int`, and a `{"count": n}` JSONResponse sent through `db.run`, so the existing `503 unavailable` handling applies. ✔

## Test review

The `reviewed acceptance tests for` commit (0202344) records `findings: 1`, which commit c90e214 resolved. It has no `unresolved:` lines.

## Mutation check (report only)

3 of 4 mutants of the changed code were caught by the acceptance tests (75 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/todo_api/todos/repository.py:41 0 → 1`
