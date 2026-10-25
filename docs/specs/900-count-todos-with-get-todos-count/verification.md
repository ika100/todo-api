# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** bf38e3b · **Base:** a300b5e · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_with_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos through `POST /todos`, asserts `200`, `Content-Type` starting with `application/json`, and body exactly `{"count": 3}` (equality, so no extra keys and an integer, not a string). The count is one `SELECT count(*) FROM todos` run through `app.state.db.run`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_with_no_todos`, `::test_count_route_does_not_shadow_patch`, `::test_count_route_does_not_shadow_delete` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:61-66`, `src/todo_api/todos/router.py:77-81` | Empty case asserts `200` and exactly `{"count": 0}` (the autouse fixture in `tests/conftest.py:74` drops the table per test, so this is also the never-used database). `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` assert `404` and the exact `todo_not_found` body; they reach the unchanged `patch_todo`/`delete_todo`, where `parse_id("count")` returns `None`. "Existing endpoints do not change": `patch_todo`, `delete_todo`, `list_todos`, `create_todo` are untouched in the diff, and the existing suite passes (`devbox run ci` green). |

Acceptance tests are unchanged since the red commit `3298ed1` (`git diff 3298ed1..HEAD -- tests` is empty).

## Non-goals

No filtering, paging or query parameters on the count route; no other endpoint changed. No schema change (`SCHEMA_SQL` untouched), no migration, configuration, gitops, `Dockerfile` or CI change. ✔

## Deviations from the plan

- All changed source files are in t1's `files` (`repository.py`, `router.py`, `README.md`); the new test file is the testers' file foreseen by the plan; spec docs are pipeline bookkeeping. t1 is `done: true`.
- `README.md`: the endpoint line was added, but the plan's note to add a link to spec 900 in the "Details" line (`README.md:31`) was not done. Acceptable: documentation only, no criterion depends on it; worth a one-line follow-up.
- `README.md` wording is `count todos (\`{"count": <int>}\`)` instead of the plan's `number of todos (\`{"count": n}\`)`. Acceptable, same meaning.

## Contract

Matches `design.md`: `GET /todos/count` returns `200 application/json {"count": <int>}` via `JSONResponse` (`router.py:47`), declared after `GET /todos` and before the `/{todo_id}` routes (`router.py:40`), with the docstring warning about a future `GET /todos/{todo_id}` (`router.py:44`). Database errors propagate unchanged through `db.run`, so the existing `503 unavailable` mapping applies (not covered by a new test; the spec's criteria do not require it). `PATCH`/`DELETE /todos/count` answer `404 todo_not_found` through the unchanged routes; PATCH keeps body-before-id order (`router.py:63-64`). ✔
