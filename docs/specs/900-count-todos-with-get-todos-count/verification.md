# Verification — 900 Count the todos with GET /todos/count

**Result:** pass
**Commit:** 33e1def · **Base:** eae60dc · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos`, `tests/test_todos_count.py::test_count_follows_creates_and_deletes` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | Creates three todos through the API against the real Postgres, then asserts `200`, `content-type` starts with `application/json`, body exactly `{"count": 3}` and `count` is a JSON integer. The second test shows the count tracks creates and deletes (2 then 1). |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_empty`, `tests/test_todos_count.py::test_count_route_does_not_clash_with_id_routes` | `src/todo_api/todos/router.py:40` (declared before `/{todo_id}` at `router.py:57`, `router.py:73`) | Empty database: asserts `200`, JSON content type, body `{"count": 0}`. Clash: `PATCH /todos/count` and `DELETE /todos/count` still answer `404 todo_not_found` (what they answered before), the existing todo is untouched (`GET /todos` unchanged, count still 1), and `PATCH`/`DELETE /todos/{id}` with a real id still answer 200/204. |

## Non-goals

No filtering, paging or query parameters on the new route; no other handler changed (the diff to `router.py` adds 6 lines only, `repository.py` adds `count_todos` only). No schema, configuration or gitops change: `main.py`, migrations and settings are untouched. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`. Acceptable: these are the acceptance tests the build writes before the code.
- `docs/specs/900-.../spec.md` status `approved` → `building` with a changelog line, and `design.md`/`plan.md` added. Acceptable: pipeline bookkeeping, no criterion changed.
- Task t1 is `done: true`; no tasks are open.

## Contract

Matches `design.md`: `GET /todos/count`, `200`, `Content-Type: application/json`, body `{"count": <int>}` with exactly one key. The count comes from `SELECT count(*) FROM todos` (`repository.py:39`), not from loading the list. Database errors go through `request.app.state.db.run`, the same path `GET /todos` uses, so the existing error handlers apply. The route is declared directly after `list_todos` and before the `/{todo_id}` routes, as the plan says. ✔

Minor, not blocking: the `RuntimeError` branch at `repository.py:41-42` is not covered. It is a defensive branch the plan asked for, and `count(*)` always returns a row.
