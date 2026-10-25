# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 34e3348 · **Base:** d83aa4e · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:51`, `src/todo_api/todos/repository.py:38` | The test creates three todos and asserts `200`, a `Content-Type` starting with `application/json`, and the exact body `{"count": 3}`, so no extra fields are allowed. The count comes from `SELECT count(*) FROM todos` and is run against real Postgres (testcontainer or `TEST_DATABASE_URL` in `tests/conftest.py`). |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:51` (GET only, declared before the id routes at `:56` and `:72`); 404 path `router.py:59-61`, `router.py:74-76` | Empty table: asserts `200 {"count": 0}`. Shadowing: the test first checks that `/count` exists (`{"count": 1}`), then asserts that `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both return `404` with the exact `todo_not_found` body. It then checks that the existing todo was not changed (`GET /todos == [keep]`). "Existing endpoints do not change" is shown by the diff: `list_todos`, `create_todo`, `patch_todo` and `delete_todo` were not touched, and the existing suites still pass under `devbox run ci`. |

## Non-goals

There is no filtering, paging or query-parameter handling on `/todos/count`. No other endpoint changed. There was no gitops, configuration, schema or migration change: `SCHEMA_SQL`, `main.py`, `errors.py`, `pyproject.toml` and the `Dockerfile` were not touched. ✔

## Deviations from the plan

- t1 is `done: true`. Every changed source file (`repository.py`, `router.py`, `README.md`) is in t1's `files`.
- `tests/test_todos_count.py` is in no task's `files`. This is acceptable: the plan says the testers write it before coding starts (red commit 9265f68), and it has not changed since that commit.
- `docs/specs/900-*/{spec,design,plan}.md` changed as part of the spec workflow (status `building`, plan, design). Acceptable.
- `repository.count_todos` raises `RuntimeError` if `count(*)` returns no row. Postgres always returns one row for `count(*)`, so this guard never runs; it only narrows the type for mypy. Acceptable.

## Contract

Matches `design.md`:
- `GET /todos/count` returns `200` `{"count": <int>}` as JSON.
- A database outage goes through the same `db.run` path as the other routes, so `503 unavailable` is unchanged.
- The route is GET-only and declared before the `/{todo_id}` routes, so `PATCH`/`DELETE` fall through to `404 todo_not_found`.
- For PATCH, body validation still runs before `parse_id` (`router.py:58`), so an invalid body still gets `422`.

The `503` path has no new test of its own. That is acceptable: no criterion asks for one, and the code uses the same `db.run` path as the existing routes. ✔
