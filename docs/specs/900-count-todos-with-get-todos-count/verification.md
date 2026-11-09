# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 108de2e · **Base:** 9217c47 · **Trace:** 2/2 criteria named by tests (`missing: []`)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-44` | Test creates three todos via `POST /todos` (each asserted `201`), then asserts `200`, media type `application/json` (parameters stripped) and the parsed body `== {"count": 3}` (exact, no extra keys). Count comes from a single `SELECT count(*) FROM todos` through `app.state.db.run`, so the 503 mapping of the other queries applies. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40-43` (GET only); unchanged `router.py:57-62` (PATCH) and `router.py:73-77` (DELETE) | Empty table is guaranteed by the autouse `_fresh_database` fixture (`tests/conftest.py`, drops `todos` per test); test asserts `200` and `{"count": 0}`. Shadowing test asserts `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both return `404` with the exact body `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, the same path `parse_id` -> `_not_found()` that any non-UUID id takes. "Existing endpoints do not change": no existing handler, `validation.py` or `errors.py` was edited (diff touches only the added route and repository function), and no existing test file changed; `devbox run ci` green. |

## Non-goals

No filtering, paging or query-parameter handling was added (`router.py:40-43` reads no query params). No change to other endpoints, no gitops, configuration, schema (`SCHEMA_SQL` untouched) or migration change. No template-owned layout touched. ✔

## Deviations from the plan

- `docs/specs/900-count-todos-with-get-todos-count/design.md` changed in commit 53d3038 (`wip(t1): interrupted`), outside every task's `files`: one blank line added between two code-block stubs (formatter-style whitespace). No content change; acceptable.
- `spec.md` status/Changelog (`building`) and `plan.md` (`done: true`) are orchestrator bookkeeping; acceptable.
- All tasks done: t1 `done: true`. Files of t1 (`repository.py`, `router.py`, `README.md`) match the change; README gained the planned endpoint line.
- Acceptance tests unchanged since red commit baa902e (`git diff baa902e..HEAD -- tests` is empty).

## Contract

Matches `design.md`: handler `count_todos(request) -> JSONResponse` on `@router.get("/count")`, declared after `list_todos` and before the `/{todo_id}` routes; repository `count_todos(conn) -> int` with `SELECT count(*) FROM todos` and `RuntimeError` on a missing row, as specified. Response body is exactly `{"count": <int>}`. ✔

Observations (not failures): the 503 path and `POST /todos/count -> 405` from the contract have no dedicated test; no criterion requires them, and both reuse existing generic handling.

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
