# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** e5e55ef · **Base:** aec442d · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos, then checks `200`, a `content-type` starting with `application/json`, and a body exactly equal to `{"count": 3}`. The count is one `SELECT count(*) FROM todos` with an `int()` conversion, as the design asks. |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (new route); `router.py:56-61` and `router.py:72-76` (unchanged `patch_todo`/`delete_todo`: `parse_id("count")` gives `None`, which raises `_not_found()`) | Empty table: `200` with body `{"count": 0}`. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` both return `404` with the full `todo_not_found` body. The test first checks that GET returns `{"count": 1}`, so the 404s cannot pass vacuously. Afterwards the count and the list still show 1, so nothing was deleted. "Existing endpoints do not change": the diff only adds code (router +5, repository +8, nothing removed), and the existing suites (`tests/test_todos_api.py`, `tests/test_todos_title_patch.py`) are untouched and pass in `devbox run ci`. |

The acceptance tests are byte-identical to red commit 53e0d8d: `git diff 53e0d8d..HEAD -- tests` is empty.

## Non-goals

No filtering, paging, or changes to other endpoints. No gitops, configuration or schema change: `SCHEMA_SQL`, `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` were not touched. ✔

## Deviations from the plan

- None in code. Every changed source file (`repository.py`, `router.py`, `README.md`) is in t1's `files`. `tests/test_todos_count.py` is the testers' acceptance file, which the plan expects. The other changes are spec docs.
- t1 is `done: true`.
- The route sits right after `list_todos` and before the `/{todo_id}` routes, as the plan says. The README adds the endpoint line and the spec 900 link, as planned.

## Contract

Matches `design.md`. `GET /todos/count` returns `200 {"count": <int>}` as JSON with no other fields. It goes through `db.run`, so a database outage gives the existing `503 unavailable`. `PATCH`/`DELETE /todos/count` return `404 todo_not_found`. ✔

RESULT: pass
