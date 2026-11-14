# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 016f4b4 · **Base:** daf8245 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `Content-Type` starts with `application/json`, parsed body `== {"count": 3}` (exact, one key) |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_count_route_does_not_shadow_id_routes`, `::test_count_does_not_change_other_endpoints` | `src/todo_api/todos/router.py:40` (GET only); `router.py:57`, `router.py:73` unchanged, `parse_id("count")` gives `todo_not_found` | empty table gives `200 {"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both `404` with the full `todo_not_found` body (`src/todo_api/errors.py:16`); list/patch/delete keep working and the count follows them; the existing suite still passes (Phase 3 `devbox run ci` green) |

## Non-goals

No filtering, paging, or change to the other handlers (diff of `router.py` adds only the `GET /count` route). No gitops, configuration or schema change; the count is `SELECT count(*) FROM todos` against the existing table. No template-owned layout touched. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`: the acceptance tests from the red commit; acceptable.
- `spec.md` (status `building`, changelog line), `plan.md`, `design.md` are in no task's `files`: pipeline documents; acceptable.
- Task t1 is `done: true`. No other deviation.

## Contract

Matches `design.md`: `GET /todos/count` answers `200 {"count": n}` as JSON through `app.state.db.run` (so the existing `503 unavailable` applies); `PATCH`/`DELETE /todos/count` answer `404 todo_not_found` through the unchanged id handlers. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
