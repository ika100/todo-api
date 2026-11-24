# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, run through `app.state.db.run` like every other query. Counting in Python after `list_todos` would download the list, which is the very thing the spec removes. No ADR: the choice is local to this feature.
- There is no `GET /todos/{id}` route, so `GET /todos/count` shadows nothing. `PATCH /todos/count` and `DELETE /todos/count` keep hitting the existing `/{todo_id}` routes. `"count"` is not a UUID, so `parse_id` returns `None` and they answer `404 todo_not_found` (AC-900.2). Starlette prefers a full match (path and method) over the partial match on the GET-only `/count` route, so neither request gets a `405`. The router code for PATCH and DELETE does not change.
- No migration, no new index, no configuration and no gitops change (non-goals).

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` takes no query parameters and no body. Query parameters are ignored: there is no filtering (non-goal).

- `200`, `Content-Type: application/json`, body `{"count": <int>}`, where `count` is a non-negative JSON integer, the number of rows in `todos` at query time. `{"count": 3}` for three todos (AC-900.1), `{"count": 0}` for none (AC-900.2).
- `503`, `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database is unreachable within the existing deadline. This is the same path and body as `GET /todos`, and the endpoint adds nothing new to it.
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body such as `{"done": true}`: `404`, `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. The body is validated first, as for any id, so an invalid body keeps answering `422 invalid_request`.
  - `DELETE /todos/count`: the same `404 todo_not_found` (AC-900.2).
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` do not change (AC-900.2).

Signatures:

```python
# repository.py
async def count_todos(conn: AsyncConnection) -> int  # SELECT count(*) FROM todos

# router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse  # JSONResponse({"count": n})
```
