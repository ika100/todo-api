# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** ac5b5aa · **Base:** 167ebf6 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `::test_count_includes_done_and_open` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-44` | Three `POST /todos`, then asserts `200`, `content-type` starting with `application/json`, decoded body `== {"count": 3}` and that `count` is an `int` (lines 16-24). The route returns `JSONResponse({"count": n})` from a single `SELECT count(*) FROM todos`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_zero_todos`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id`, `::test_existing_list_endpoint_unchanged`, `::test_count_ignores_query_parameters` | `src/todo_api/todos/router.py:40` (GET only), `router.py:57-62` and `router.py:73-77` (unchanged `parse_id` -> `404`) | Zero case asserts `200` and `{"count": 0}` (lines 36-42). `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` and the full `todo_not_found` body (lines 52-61). The router diff only adds lines; `patch_todo`/`delete_todo` are untouched. The "existing endpoints do not change" part is covered by `test_existing_list_endpoint_unchanged` together with the unchanged regression suites `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` (no diff since base), which pass in `devbox run ci`. |

## Non-goals

There is no filtering or paging: query parameters are ignored (`test_count_ignores_query_parameters`), and no other endpoint changed. There is no gitops, configuration, schema or migration change (`SCHEMA_SQL` is untouched). The template-owned layout is unchanged too; this service has no UI. ✔

## Deviations from the plan

- `docs/specs/900-.../design.md` changed in `d6fc2dd` ("wip(t1): interrupted"), but it is in no task's `files`. The change is one blank line inside a code block (formatting only, no contract change). Acceptable.
- `spec.md` (status `building`, changelog line) and `plan.md` (`done: true`) were changed by the pipeline's own bookkeeping commits. Acceptable.
- Task t1 is `done: true`. Its `files` (`repository.py`, `router.py`, `README.md`) match the code changes. ✔
- `tests/test_todos_count.py` is unchanged since the red commit `77ab871`. ✔

## Contract

The build matches `design.md`. The signatures are `count_todos(conn: AsyncConnection) -> int` and `@router.get("/count") count_todos(request) -> JSONResponse`. The route sits above the `/{todo_id}` routes, and no PATCH/DELETE handler exists for `/count`. The body has the single key `count`, typed as an integer. Database errors go through `Database.run` unchanged. A missing row raises `RuntimeError`, as the plan asks. The README entry and the spec 900 link were added as planned. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
