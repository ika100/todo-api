# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** e267d55 · **Base:** 9db5602 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Test creates 3 todos via `POST /todos` (each asserted 201), then asserts status 200, `content-type` starts with `application/json`, and body exactly `{"count": 3}`. Handler returns `JSONResponse({"count": n})`, where `n` comes from `SELECT count(*) FROM todos` cast to `int`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77`, `src/todo_api/todos/validation.py:67` | Empty-store test asserts 200 and exactly `{"count": 0}`. The shadowing test sends `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count`, and asserts 404 with the full `todo_not_found` body for both. `parse_id("count")` returns `None`, so the existing handlers raise `_not_found()`. The diff does not touch those handlers. "Existing endpoints do not change": the only router change is the new `/count` route (lines 40-43). `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are unchanged and pass in the green `devbox run ci` run. |

## Non-goals

The change adds no filtering, paging or query parameters to the count route. The other endpoints are unchanged: the diff only adds lines in `router.py` and `repository.py`. It changes no gitops, configuration or schema files. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is not listed in t1's `files`. This is acceptable because it is the acceptance-test file from the red commit `f6b2ef3`, not the coder's work.
- The only other changes outside task files are `docs/specs/900-.../{design,plan,spec}.md`, which are spec workflow artifacts. Acceptable.
- Task t1 is `done: true`. No task is still open.

## Contract

The build matches `design.md`. `GET /todos/count` answers `200 application/json {"count": <int>}` with no other fields, and the count comes from a single `SELECT count(*) FROM todos` (`repository.py:38-43`). Errors still go through the existing `request.app.state.db.run` path, so the `503 unavailable` behaviour is inherited and unchanged; no test covers it, and the spec does not require one. `PATCH`/`DELETE /todos/count` keep the `404 todo_not_found` result. The literal `/count` route has no conflict because no `GET /todos/{todo_id}` route exists. ✔
