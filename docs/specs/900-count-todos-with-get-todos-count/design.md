# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with one `SELECT count(*) FROM todos`, never by loading the list: the point of the endpoint is to avoid transferring the rows (Problem).
- `GET /todos/count` is a static route on the existing `/todos` router. It is GET-only. There is no `GET /todos/{id}`, so nothing can shadow it, and it cannot shadow the id routes: Starlette treats a path match with the wrong method as a partial match and keeps looking, so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo`, where `parse_id("count")` is `None` and they answer `404 todo_not_found` (AC-900.2). No change to those handlers.
- No ADR: the decision is local to this feature.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int >= 0>}`. Exactly one key. `count` is a JSON integer, the number of rows in `todos` at the time of the query (AC-900.1, AC-900.2).
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database misses the deadline, the same mapping as every other `/todos` route (via `db.run`).
- Other methods on `/todos/count`: unchanged behaviour of the id routes. `PATCH /todos/count` with `{"done": true}` and `DELETE /todos/count` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` (AC-900.2). `PATCH` with an invalid body keeps answering the body-validation error first, as for any id. `POST /todos/count` → `405` `method_not_allowed`, as for any other id path.

Repository signature:

```python
async def count_todos(conn: AsyncConnection) -> int  # SELECT count(*) FROM todos
```

## Data

No schema change, no migration. `count(*)` on `todos`.

## Risks

- `count(*)` is a sequential scan on a large table. Acceptable for a todo list; no filtering or caching (non-goals).
