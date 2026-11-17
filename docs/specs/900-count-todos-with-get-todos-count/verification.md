# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 05d7449 · **Base:** 1a6645b · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates 3 todos, asserts `200`, `content-type` starts with `application/json`, body `== {"count": 3}` (exact, single key) |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_count_does_not_shadow_id_routes`, `::test_count_route_registered_and_id_routes_kept` | `src/todo_api/todos/router.py:40` (static route above `/{todo_id}`); unchanged `router.py:57-70` (`patch_todo`), `router.py:73-84` (`delete_todo`) via `parse_id` -> `_not_found()` | empty DB (per-test `DROP TABLE`, `tests/conftest.py:74`) -> `{"count": 0}`; `PATCH /todos/count {"done": true}` and `DELETE /todos/count` -> `404` with the exact `todo_not_found` body (message matches `src/todo_api/errors.py:16`); existing endpoints unchanged in the diff and their suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) untouched and green per the Phase 3 run |

## Non-goals

No filtering, paging, or change to other endpoints: `patch_todo`, `delete_todo`, `list_todos`, `create_todo` are untouched. No gitops, configuration, schema or migration change (`SCHEMA_SQL` unchanged, no Dockerfile change). No template-owned layout change. ✔

## Deviations from the plan

- `docs/specs/900-count-todos-with-get-todos-count/spec.md` (status `approved` -> `building`, changelog line), `design.md`, `plan.md` changed outside t1's `files`: pipeline bookkeeping and planning artifacts, no criterion changed; acceptable.
- All tasks (`t1`) are `done: true`. ✔

## Contract

Matches `design.md`: `GET /todos/count` -> `200 {"count": n}` with `application/json`, computed by one `SELECT count(*) FROM todos` through `db.run` (so the existing `DatabaseUnavailable` -> `503` path applies as for `GET /todos`); `PATCH`/`DELETE /todos/count` -> `404 todo_not_found`. README documents the endpoint as planned. ✔

## Mutation check (report only)

3 of 4 mutants of the changed code were caught by the acceptance tests (75 %; spec 152, report only).

Survived (a test that names the criterion would fail if it checked this):
- `src/todo_api/todos/repository.py:41 0 → 1`
