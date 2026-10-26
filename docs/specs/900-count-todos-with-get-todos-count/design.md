# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is computed in the database with one `SELECT count(*) FROM todos`, not by loading the list and taking its length: the point of the endpoint is to avoid moving every row (Problem).
- The route is a static `GET` path on the existing `/todos` router, declared before the `/{todo_id}` routes. There is no `GET /todos/{id}`, so nothing is shadowed today; declaring the static path first keeps it unambiguous if one is added. `PATCH` and `DELETE` on `/todos/count` keep matching the existing `/{todo_id}` routes (Starlette prefers a full method match over the path-only match of the GET route), where `parse_id("count")` fails and they answer `404 todo_not_found` exactly as for any unknown id (AC-900.2). No change to those handlers.
- No ADR: the decision is local to this endpoint.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body)

- `200`, `Content-Type: application/json`, body `{"count": <int>}` where `count` is a non-negative integer equal to the number of todos currently stored, done or not (AC-900.1, AC-900.2). The body has exactly the one key `count`.
- `503` with the existing error body `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached within the existing deadline (same behaviour as `GET /todos`, via `Database.run`).
- Other methods on `/todos/count` are unchanged from today (AC-900.2):
  - `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. (An invalid body still answers `422 invalid_request` first, as for any id, per spec 002's rule order.)
  - `DELETE /todos/count` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`.
  - `POST /todos/count` and `PUT /todos/count` → `405` `method_not_allowed`, as today for any `/todos/{x}` path without that method.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}` are unchanged.

Repository signature:

```python
async def count_todos(conn: AsyncConnection) -> int  # SELECT count(*) FROM todos
```

## Data

No schema change, no migration. `count(*)` on `todos` uses the existing table; no new index is needed.

## Risks

- `count(*)` is a sequential or index-only scan; acceptable for a todo list's size. Revisit only if the table grows large (out of scope).
