# Verification — 900 Count the todos with GET /todos/count

**Commit:** fd61456 · **Base:** b5d0650 · **Trace:** 2/2 criteria named by tests

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-900.1 | met | `tests/test_todos_count.py::test_count_three_todos` | `src/todo_api/todos/router.py:40`, `src/todo_api/todos/repository.py:38` | creates three todos, asserts `200`, `content-type` starting with `application/json`, and parsed body `== {"count": 3}`; counted with `SELECT count(*)` as the design says |
| AC-900.2 | met | `tests/test_todos_count.py::test_count_no_todos`, `tests/test_todos_count.py::test_count_route_does_not_shadow_id_routes` | `src/todo_api/todos/router.py:40` (GET `/count` declared before `/{todo_id}` at `:56`, `:72`), `src/todo_api/todos/router.py:59-61`, `:74-76` | empty DB gives `200` `{"count": 0}`; `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` give `404` with the exact `todo_not_found` body; the existing todo survives and the count stays 1. PATCH/DELETE handlers unchanged in the diff; existing `tests/test_todos_api.py` green in `devbox run ci` |

## Non-goals

No filtering, paging or change to other endpoints (diff to `router.py` adds only the new route); no gitops, configuration or schema change. No template-owned layout change. ✔

## Deviations from the plan

- `tests/test_todos_count.py` is in no task's `files`: the acceptance test file written from the spec before the code; acceptable.
- `docs/specs/900-.../{spec,plan,design}.md` changed: pipeline artifacts (status `building`, plan `done: true`); acceptable.
- Task t1 has `done: true`. Handler is named `count_todos_route` instead of the pseudocode's `count_todos` (avoids clashing with the repository name); behaviour matches the contract; acceptable.

## Contract

Matches `design.md`: `GET /todos/count` → `200` `{"count": int}` as JSON; `503` through the shared `db.run` path, unchanged. ✔

**Result:** pass

## Mutation check (report only)

4 of 4 mutants of the changed code were caught by the acceptance tests (100 %; spec 152, report only).
