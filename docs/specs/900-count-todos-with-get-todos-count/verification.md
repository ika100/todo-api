# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 61ed8f2 · **Base:** c6d414f · **Trace:** 2/2 criteria named by tests (`missing: []`)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-43` | The test creates three todos through `POST /todos` (each asserted `201`), then asserts `200`, a `content-type` starting with `application/json`, and the parsed body `== {"count": 3}`, so no extra keys pass. The route returns `JSONResponse({"count": n})`. `n` comes from one `SELECT count(*) FROM todos`, cast with `int(row[0])`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40-43`, unchanged `router.py:57-62` (PATCH) and `router.py:73-77` (DELETE) | Empty state comes from the per-test `DROP TABLE` in the `client` fixture. The test asserts `200`, the body `== {"count": 0}` and that `count` is an `int`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` are each asserted `404` with `error.code == "todo_not_found"` and `error.message == "This todo no longer exists"`, which equals `MSG_TODO_NOT_FOUND` (`src/todo_api/errors.py:16`). Both handlers are unchanged. `parse_id("count")` returns `None`, so they raise the same `_not_found()` (`router.py:30-31`) used for any id that is not a UUID. That makes the response identical to an unknown id by construction. "Existing endpoints do not change": the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) are unchanged and green, and the diff touches no other handler. Nit, not a failure: `assert_not_found` checks `code` and `message`, not full-body equality the way `test_todos_api.py:17` does. |

## Non-goals

- No filtering or paging: the handler reads no query parameters (`router.py:41-43`). ✔
- No change to other endpoints: the router diff only adds lines 40-44. `list_todos`, `create_todo`, `patch_todo`, `delete_todo` and `validation.py` are unchanged. ✔
- No gitops, configuration or schema change: `SCHEMA_SQL`, `pyproject.toml`, `Dockerfile`, CI and env vars are untouched. ✔
- No template-owned layout touched (API service, no pages). ✔

## Deviations from the plan

- `tests/test_todos_count.py`: not in t1's `files`, but it is the acceptance-test file the testers wrote in the red commit `959dafe`, as the plan intends. Acceptable.
- `docs/specs/900-.../{spec,plan,design}.md`: pipeline bookkeeping (plan and design created, spec status set to `building` with a Changelog entry). The criteria text is unchanged. Acceptable.
- All tasks are `done: true` (t1). The README line matches the plan's wording exactly.

## Contract

Matches `design.md`:

- `200 application/json {"count": <int>}` with no other keys.
- The count is a single `SELECT count(*)`, not `len(list_todos())` (`repository.py:39`).
- The query goes through `request.app.state.db.run`, so database failures and the deadline map to `503 unavailable` the same way `GET /todos` does (`router.py:42`).
- The neighbouring PATCH and DELETE routes are unchanged, so `POST` and `PUT` on `/todos/count` still answer `405` as before. No acceptance test is needed for these because the spec does not state them.

✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
