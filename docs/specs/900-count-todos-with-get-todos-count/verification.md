# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** c8072d1 · **Base:** 910580c · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `tests/test_todos_count.py::test_count_includes_done_todos` | `src/todo_api/todos/router.py:40-43`, `src/todo_api/todos/repository.py:38-43` | The first test creates three todos through `POST /todos` and asserts status `200`, media type `application/json` and body exactly `{"count": 3}`. The second test checks that done todos are counted, that an unknown query parameter (`done=false`) is ignored, and that the count equals `len(GET /todos)`. The count comes from a single `SELECT count(*) FROM todos` run through `Database.run`, returned as `int(row[0])`. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `::test_patch_count_is_not_found`, `::test_delete_count_is_not_found` | `src/todo_api/todos/router.py:40` (static route), `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` (unchanged id handlers) | With no todos the response is `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both get `404` with the full `todo_not_found` body (code and message compared exactly). They reach the existing handlers, where `parse_id("count")` returns `None` and raises `_not_found()`. The diff adds no PATCH or DELETE handler for `/count`. "Existing endpoints do not change": the router diff only adds lines, `tests/test_todos_api.py` and `tests/test_todos_title_patch.py` are not modified, and `devbox run ci` is green. |

## Non-goals

No filtering or paging was added: the count handler reads no query parameters (`router.py:41-43`). No other endpoint changed. No gitops, config, schema or migration change: `SCHEMA_SQL` is untouched and no env vars were added. ✔

## Deviations from the plan

- None in code. All changed source files (`repository.py`, `router.py`, `README.md`) are in t1's `files`. `tests/test_todos_count.py` is the acceptance test file the plan asks for. The files under `docs/specs/900-.../` are spec artifacts. t1 is `done: true`.
- Acceptance tests have not changed since the red commit `053a78d` (`git diff 053a78d..HEAD -- tests` is empty).

## Contract

Matches `design.md`. The response is `200 application/json {"count": <int>}` from `SELECT count(*)`. The route is declared before the `{todo_id}` routes. Unknown query parameters are ignored. PATCH and DELETE on `/count` return `404 todo_not_found` through the unchanged handlers, and in PATCH body validation still runs before `parse_id` (`router.py:59-60`). The README line was added as specified. The `503 unavailable` path is inherited from `Database.run` and has no count-specific test. The spec has no criterion for it, so this does not affect the verdict. ✔
