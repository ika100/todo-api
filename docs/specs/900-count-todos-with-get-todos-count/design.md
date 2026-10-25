# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in Postgres with `SELECT count(*) FROM todos`, not by loading the list: the point of the endpoint is to avoid materializing every row (Problem).
- The route lives in the existing `todos/router.py` (`APIRouter(prefix="/todos")`) as `@router.get("/count")`, declared before the `/{todo_id}` routes. There is no `GET /todos/{todo_id}`, so the literal path cannot be captured by a parameter route; `PATCH`/`DELETE /todos/count` keep their current behaviour (handled by the `/{todo_id}` routes, which answer `404 todo_not_found` for a non-UUID id) (AC-900.2).
- No ADR: the change is feature-local and follows the existing router/repository pattern.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}` where `count` is a non-negative JSON integer equal to the number of rows in `todos` at query time. Exactly one key. (AC-900.1, AC-900.2)
- Examples: three todos → `{"count": 3}`; no todos → `{"count": 0}`.
- Database unavailable: same behaviour as `GET /todos` (the existing error handlers apply; no new error code).

Unchanged: `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`.

## Data

No schema change. Reads the existing `todos` table.

## Risks

- `count(*)` is a full scan on large tables; acceptable at todo-list scale and still far cheaper than serializing the list.
