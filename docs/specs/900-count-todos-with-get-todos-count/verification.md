# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 5519f36 · **Base:** 4a9c4d7 · **Trace:** 2/2 criteria named by tests (missing: none)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:51-54`, `src/todo_api/todos/repository.py:50-55` | Creates three todos (each asserted `201`), then asserts `200`, `content-type` starting with `application/json`, decoded body `== {"count": 3}` (so no extra keys) and `count` is an `int`. Real Postgres via the `client` fixture, so the `SELECT count(*)` path is exercised. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_zero_and_id_routes_not_shadowed`; unchanged existing suite `tests/test_todos_api.py`, `tests/test_todos_title_patch.py` | `src/todo_api/todos/router.py:51` (GET-only route), `router.py:57-62`, `router.py:73-77` (unchanged id handlers, `parse_id("count")` -> `_not_found()`, `router.py:30-31`) | Asserts empty DB `200 {"count": 0}` (int); `PATCH /todos/count` with `{"done": true}` -> `404` with body equal to the full `todo_not_found` envelope; `DELETE /todos/count` -> `404` with the same body. The expected body is the same `NOT_FOUND` constant `tests/test_todos_api.py:17` uses for unknown ids, so "exactly as for any unknown id" is asserted. "Existing endpoints do not change": the diff touches no existing handler (`git diff` adds lines 51-56 only), and the existing acceptance suites pass unchanged (`cplat quiet ci` green). |

## Non-goals

No filtering, paging or query-parameter handling was added; no other endpoint changed (`patch_todo`, `delete_todo`, `list_todos`, `create_todo`, `to_json`, `errors.py` untouched). No gitops, configuration, schema or migration change (`SCHEMA_SQL` untouched). No template-owned layout changed (service has no UI; `Dockerfile`, CI, `devbox.json`, `CLAUDE.md` untouched). ✔

## Deviations from the plan

- `docs/specs/900-.../design.md` changed in `56461fe` (whitespace-only reformat of the pseudocode by an interrupted run), outside every task's `files`; acceptable: no content or contract change.
- `docs/specs/900-.../spec.md` status `approved` -> `building` plus Changelog line; acceptable: orchestrator bookkeeping, criteria unchanged.
- `tests/test_todos_count.py` is in no task's `files`; acceptable: the plan assigns it to the testers (RED commit `b7db12c`), unchanged since.
- Every task has `done: true` (t1). ✔
- `repository.count_todos` adds the `RuntimeError` on a `None` row the plan asks for (beyond the design pseudocode); acceptable, plan-mandated.

## Contract

Matches `design.md`: `@router.get("/count")` only (no `api_route`, no catch-all), placed before the `/{todo_id}` handlers; one `SELECT count(*) FROM todos` through `Database.run` (same deadline and `503 unavailable` mapping as the other routes); body `{"count": <int>}` via `JSONResponse`. The `503` path for this route has no dedicated test; it is not a criterion and reuses the shared `Database.run` mapping. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
