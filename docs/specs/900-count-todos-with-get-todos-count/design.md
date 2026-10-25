# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, not `len(list_todos())`. Loading every row just to count them is the cost the spec is meant to remove.
- The route is a static `@router.get("/count")` on the existing `/todos` router, declared before the `/{todo_id}` routes. No `GET /todos/{todo_id}` route exists, and Starlette keeps searching after a path match with the wrong method. So `PATCH /todos/count` and `DELETE /todos/count` still go to the id handlers. Those handlers reject `count` in `parse_id` and answer `404 todo_not_found` (AC-900.2). Neither id handler changes.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count`, no query parameters, no request body.

- `200`, `Content-Type: application/json`, body exactly `{"count": <int>}`. The value is a JSON integer ≥ 0 and the body has no other keys. With three todos the body is `{"count": 3}` (AC-900.1). With none it is `{"count": 0}` (AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database does not answer within the existing 2.5 s deadline. This is the same path as every other `/todos` endpoint: `Database.run` raises `DatabaseUnavailable`.
- Query parameters are ignored (filtering is a non-goal).

Unchanged id routes (AC-900.2):

- `PATCH /todos/count` with body `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
- `DELETE /todos/count` → `404` with the same body.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` keep their spec 001/002 contracts.

## Data

No schema change. The count is a `SELECT count(*) FROM todos` read inside `Database.run`. That run commits the read like any other operation.

## Risks

- Route order: if `/count` ever moves behind a future `GET /{todo_id}`, the id route would shadow it. To guard against that, the route is declared first and the AC-900 tests cover it.
