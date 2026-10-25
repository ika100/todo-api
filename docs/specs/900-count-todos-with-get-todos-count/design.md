# Design — 900 Count the todos with GET /todos/count

Builds on [001's design](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002's design](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid; only the additions below are new.

## Decisions

- **One `SELECT count(*)` in the repository, one GET route in the existing router.** `repository.count_todos(conn) -> int` runs `SELECT count(*) FROM todos` and the route answers `{"count": n}`. The database counts; the API never loads rows to count them (the spec's Problem).
- **The route is registered for `GET` only, at the literal path `/todos/count`.** Starlette prefers a route that matches path *and* method over one that matches only the path, so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo` with `todo_id="count"`. `parse_id("count")` is `None`, so both answer `404 todo_not_found` exactly like any non-UUID id (AC-900.2). The coder must not add `PATCH`/`DELETE` handlers, a `/{todo_id}` GET route or any method-not-allowed handling for `/todos/count`.
- **It goes through `Database.run`** like every other operation, so the 2.5 s deadline and the `503 unavailable` mapping apply unchanged.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `async def count_todos(conn: AsyncConnection) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler `count_todos` | changed |
| `README.md` | endpoint list mentions `GET /todos/count`, link to spec 900 | changed |

## Contract

### `GET /todos/count`

- `200`, `Content-Type: application/json`, body exactly `{"count": <int>}`: a JSON integer >= 0 equal to the number of rows in `todos` at the time of the request; no other keys (AC-900.1, AC-900.2).
- Query parameters are ignored (no filtering, no paging: non-goals).
- Database unreachable or slower than 2.5 s: `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`, as for every other endpoint.

### Unchanged neighbours (AC-900.2)

| Request | Response |
|---|---|
| `PATCH /todos/count` with `{"done": true}` | `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` |
| `DELETE /todos/count` | `404 {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}` |
| `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready` | unchanged from 001/002 |

A `PATCH /todos/count` with an invalid body still follows 002's rule order (body rules before the id), so it answers `422`, as for any other non-UUID id.

### Test harness

No new fixtures. The acceptance tests go in a new file (e.g. `tests/test_todos_count.py`) and reuse `tests/conftest.py`'s `client`. Existing test files are not modified.

## Data

No change. No migration, no index (`count(*)` on a todo list is a sequential scan of a small table).

## Risks

- None worth mitigating: a full-table count is O(rows); acceptable at this service's size.
