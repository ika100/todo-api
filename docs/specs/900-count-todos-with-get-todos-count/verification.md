# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 8b27ecc · **Base:** aac9745 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-42`, `src/todo_api/todos/repository.py:38-44` | creates 3 todos; asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}`. Count computed with `SELECT count(*) FROM todos`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `::test_count_does_not_shadow_patch`, `::test_count_does_not_shadow_delete` | `src/todo_api/todos/router.py:40` (GET only), `src/todo_api/todos/router.py:56-61,72-76` (unchanged `parse_id` -> `todo_not_found`) | empty DB (autouse `_fresh_database` drops the table) -> `200 {"count": 0}`; `PATCH /todos/count {"done": true}` and `DELETE /todos/count` -> `404` with the exact `todo_not_found` body (`MSG_TODO_NOT_FOUND`, `src/todo_api/errors.py:16`); DELETE test also asserts the existing todo survives. "Existing endpoints do not change": the diff touches no existing handler, and the existing suite passes (`cplat quiet ci` green). |

## Non-goals

No filtering, paging or query parameters; no change to other endpoints, error handlers, schema, configuration or gitops. No template-owned layout touched. ✔

## Deviations from the plan

- `src/todo_api/db.py` changed but is in no task's `files`: a comment moved to its own line by `lint-fix` (no behaviour change); acceptable.
- All tasks `done: true`. ✔

## Contract

Matches `design.md`: `GET /todos/count` -> `200` JSON `{"count": int}` via `request.app.state.db.run` (so the existing `503 unavailable` path applies); no `PATCH`/`DELETE` handler for `/count`, so those fall through to `/{todo_id}` and answer the specified `404 todo_not_found`. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
