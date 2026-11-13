# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 301b358 · **Base:** 2e0190f · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `content-type` starts with `application/json`, parsed body `== {"count": 3}`; count comes from `SELECT count(*) FROM todos` through `db.run`, as the design requires |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_count_route_does_not_shadow_id_routes`, `::test_existing_endpoints_unchanged_by_count` | `src/todo_api/todos/router.py:40`, `:56-61`, `:72-76` (unchanged `parse_id` → `todo_not_found`) | asserts `200 {"count": 0}` on an empty database (autouse `_fresh_database` drops the table); `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both asserted `404` with the full `todo_not_found` body; `GET /todos` and `DELETE /todos/{id}` checked alongside; the unchanged `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` pin the rest of the existing contracts and pass in the green `devbox run ci` |

## Non-goals

No filtering, paging or query-parameter handling was added; the other handlers (`list_todos`, `create_todo`, `patch_todo`, `delete_todo`) are unchanged in the diff. No gitops, configuration, schema or `SCHEMA_SQL` change. No template-owned layout change. ✔

## Deviations from the plan

None. Every changed source file (`repository.py`, `router.py`, `README.md`) is in t1's `files`; `tests/test_todos_count.py` is the acceptance test file the plan assigns to the testers; the spec-directory documents are the spec's own. t1 is `done: true`. README text matches the plan's wording.

## Contract

Matches `design.md`: `GET /todos/count` → `200` JSON `{"count": <int>}`, via `db.run` (so the existing `503 unavailable` mapping applies); `PATCH`/`DELETE /todos/count` → `404 todo_not_found` through the unchanged `parse_id` path. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
