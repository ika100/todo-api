# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 0bafaa4 · **Base:** 202efaa · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-43` | Creates 3 todos via `POST /todos`, asserts `200`, `content-type` starts with `application/json`, body exactly `{"count": 3}`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_patch_count_is_todo_not_found`, `::test_delete_count_is_todo_not_found`, `::test_existing_endpoints_unchanged` | `src/todo_api/todos/router.py:40` (GET only), `router.py:57-62` (PATCH: `parse_id("count")` is `None` → `_not_found()`), `router.py:73-77` (DELETE, same) | Empty DB → `200 {"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` → `404` with the exact `todo_not_found` body. "Existing endpoints do not change": no existing handler or existing test file changed in the diff, and the full suite (164 tests) passes. |

## Non-goals

No filtering, paging or query-parameter handling; no change to other handlers (diff of `router.py` only adds the `GET /count` handler). No migration, `SCHEMA_SQL`, configuration, `pyproject.toml`, Dockerfile, CI or gitops change. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`: it is the acceptance test file written by the testers before coding, as the plan states. Acceptable.
- `docs/specs/900-.../{spec.md,design.md,plan.md}` changed: status/changelog update, planning commits, and a ruff-format blank line in a design.md code block. Acceptable.
- Task t1 is `done: true`. No undone tasks.
- `repository.py:42` (defensive `RuntimeError` on a missing row) is uncovered; it is what the plan asked for (mirrors `create_todo`). Acceptable.

## Contract

Matches `design.md`: `count_todos(conn) -> int` runs `SELECT count(*) FROM todos` through `Database.run` (same deadline and `503 unavailable` mapping); the route is a literal `@router.get("/count")` on the existing router with no reordering; response is `JSONResponse({"count": n})` with no other keys; README gains the endpoint line and the spec 900 link. ✔
