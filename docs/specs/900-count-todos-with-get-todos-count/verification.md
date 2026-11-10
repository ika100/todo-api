# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 442d648 · **Base:** 47206e6 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_of_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos via `POST /todos`, asserts `200`, `content-type` starting with `application/json` and parsed body `== {"count": 3}` (exact, no extra keys). Count runs `SELECT count(*) FROM todos` through `Database.run` as designed. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_of_no_todos`, `::test_patch_count_is_unknown_id`, `::test_delete_count_is_unknown_id`; unchanged `tests/test_todos_api.py`, `tests/test_todos_title_patch.py` | `src/todo_api/todos/router.py:40` (static route before the id routes), `src/todo_api/todos/router.py:57-62`, `:73-77` (unchanged `parse_id` -> `_not_found`) | Empty table asserts `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` assert `404` with the full `todo_not_found` body, the same body `tests/test_todos_api.py:17` uses for unknown ids. "Existing endpoints do not change": `patch_todo`, `delete_todo`, `list_todos`, `create_todo` are untouched in the diff and the existing suites pass unmodified (CI green). |

## Non-goals

No filtering, paging or query-parameter handling was added; no other endpoint changed; no gitops, configuration, schema or migration change (`SCHEMA_SQL` untouched). No template-owned layout applies (API service). ✔

## Deviations from the plan

None. Every changed source file (`repository.py`, `router.py`, `README.md`) is in t1's `files`; `tests/test_todos_count.py` is the testers' acceptance file named by the design's test harness section; the spec/plan/design changes are pipeline bookkeeping. t1 is `done: true`. The route sits directly after `list_todos` as planned.

## Contract

Matches `design.md`: `count_todos(conn: AsyncConnection) -> int` raising `RuntimeError` on no row (`repository.py:38-43`), `@router.get("/count") async def count_todos(request) -> JSONResponse` returning `{"count": n}` (`router.py:40-43`), README line and spec 900 link added. ✔

Suppressions and tightened tests: none reported, none found in the diff (acceptance file unchanged since red commit 9e5b4a0).

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
