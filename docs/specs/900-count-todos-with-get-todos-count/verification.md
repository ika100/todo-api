# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** a759475 · **Base:** 871e395 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates 3 todos via `POST /todos`, asserts `200`, `content-type` starts with `application/json`, decoded body `== {"count": 3}` (exact dict, so exactly one key). Count is one `SELECT count(*) FROM todos` through `db.run`, as the design requires. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/router.py:57-62`, `src/todo_api/todos/router.py:73-77` | Empty table gives `200 {"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both assert `404` with the full `todo_not_found` body; `"count"` fails `parse_id` in the unchanged handlers. The test also checks the existing todo survives (`GET /todos` unchanged, count 1). "Existing endpoints do not change": the diff only adds lines to `router.py`/`repository.py`, and the existing suite passes (`cplat quiet ci` green). |

## Non-goals

No filtering, paging, query parameters or changes to other endpoints; no schema (`SCHEMA_SQL` untouched), configuration or gitops change. Template-owned layout untouched (API service, no header/footer/navigation). ✔

## Deviations from the plan

- None. Changed source files (`repository.py`, `router.py`, `README.md`) are all in t1's `files`; `tests/test_todos_count.py` is the acceptance test file written by the testers (plan: "a new file before coding"); spec/plan/design edits are pipeline bookkeeping. t1 is `done: true`.
- Note (not a deviation of this build): the tester reported a timing-based test in `tests/test_todos_api.py` that flaked in 2 earlier runs and passed on re-run; that file is not touched by this change.

## Contract

Matches `design.md`: `GET /todos/count` → `200 {"count": n}` as `JSONResponse` (`application/json`); 503 mapping inherited from `Database.run`; `PATCH`/`DELETE /todos/count` → `404 todo_not_found` without handler changes; README line added as specified. ✔

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
