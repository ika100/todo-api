# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with `SELECT count(*) FROM todos`. Loading the rows and counting them in Python would defeat the point of the endpoint (AC-900.1).
- The route is declared on the existing `todos` router as `@router.get("/count")`, placed **above** the `/{todo_id}` routes in `router.py`. Today no `GET /todos/{todo_id}` route exists, so nothing could shadow `/count` for GET. Putting it first still keeps it safe if a `GET /{todo_id}` is added later. The route is GET-only. For `PATCH`/`DELETE /todos/count`, Starlette only finds a partial match on `/count` (the path matches, the method does not) and keeps looking. The full match on `/{todo_id}` then wins, `parse_id("count")` returns `None`, and the client gets the existing `404 todo_not_found` (AC-900.2). No `405` comes from `/count`.
- There is no ADR: the decision applies only to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler, declared before the id routes | changed |

`main.py` and `errors.py` do not change: the router is already included and the error body already exists.

## Contract

`GET /todos/count`
- `200`, `Content-Type: application/json`, body `{"count": <int ≥ 0>}`, for example `{"count": 3}` with three todos (AC-900.1) and `{"count": 0}` with none (AC-900.2). The body has no other fields.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached. This is the same `db.run` path as every other todo route, unchanged.
- Query parameters are ignored. There is no filtering or paging (non-goal).

`PATCH /todos/count` with any body that `parse_patch` accepts (for example `{"done": true}`), and `DELETE /todos/count`:
- `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, the same answer as for any non-UUID id (AC-900.2). Body validation still runs first for PATCH, as today. An invalid body therefore still gets `422`, which is unchanged behaviour.

Every other endpoint (`GET`/`POST /todos`, `PATCH`/`DELETE /todos/{id}`, `/health`, `/ready`, `/ping`, `/metrics`) keeps its current behaviour (AC-900.2).

## Data

No schema change and no migration. The query is `SELECT count(*) FROM todos`, and the result is returned as a Python `int`.

## Risks

- `count(*)` scans the whole table. That is fine at todo-list sizes. If the table ever grows large, a later spec can revisit it.
