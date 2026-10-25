# Design — 900 Count the todos with GET /todos/count

Builds on [001's design](../001-todo-rest-api-list-create-mark-done-not/design.md) and [002's design](../002-change-a-todo-s-title-through-patch/design.md). Everything there stays valid; only the additions below are new.

## Decisions

- **Count in the database with `SELECT count(*) FROM todos`.** One scalar row instead of loading every todo into the service: this is the point of the endpoint (Problem). It runs through `Database.run` like every other query, so it gets the same 2.5 s deadline and `503 unavailable` mapping.
- **A literal `GET /count` route on the existing `/todos` router, no route reordering.** There is no `GET /todos/{id}` route, so nothing can shadow `GET /todos/count`, and the new route registers only `GET`. Starlette keeps searching after a path match with the wrong method, so `PATCH /todos/count` and `DELETE /todos/count` still reach `patch_todo` / `delete_todo`. There, `parse_id("count")` returns `None` and they answer `404 todo_not_found` as for any non-UUID id (AC-900.2). No change to those handlers.
- **No filtering, paging, caching, migration, index or configuration change** (Non-goals). `count(*)` on the `todos` table is fine at this service's size.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list gains `GET /todos/count` | changed |

```python
# todos/repository.py
async def count_todos(conn: AsyncConnection) -> int: ...  # SELECT count(*) FROM todos

# todos/router.py
@router.get("/count")
async def count_todos(request: Request) -> JSONResponse: ...
```

## Contract

### `GET /todos/count`

| Situation | Response | Criteria |
|---|---|---|
| any number `n >= 0` of todos | `200`, `Content-Type: application/json`, body exactly `{"count": n}` (`n` a JSON integer, no other keys) | AC-900.1, AC-900.2 |
| database unreachable or slower than 2.5 s | `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` | (unchanged behaviour of every DB-backed route) |

- `count` counts every todo, done or not. Query parameters are ignored.
- The request body, if any, is ignored.
- Other methods on `/todos/count`:
  - `PATCH /todos/count` with a valid body (e.g. `{"done": true}`) → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`, without database access. An invalid body still gets the 422 of 002's rule order first, exactly like any non-UUID id (AC-900.2).
  - `DELETE /todos/count` → `404` with the same `todo_not_found` body, without database access (AC-900.2).
  - `POST /todos/count`, `PUT /todos/count` → `405 method_not_allowed`, as for any `/todos/{id}` path today.
- `GET /todos`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `/health`, `/ready`, the serialization and the error body format do not change (AC-900.2).

### Test harness

No new fixtures. The acceptance tests go in a new file (e.g. `tests/test_todos_count.py`) and use the existing `client` fixture from `tests/conftest.py`; create the todos with `POST /todos`. Existing test files are not modified.

## Data

No change. No migration.

## Risks

- None worth noting: read-only, one scalar query, no new dependency.
