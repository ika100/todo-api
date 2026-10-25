# Design — 900 Count the todos with GET /todos/count

## Decisions

- The count is one `SELECT count(*) FROM todos` in the repository, run through `app.state.db.run` like every other todo operation. Counting in Python after `list_todos` would move every row just to count it, which is the cost the spec removes. No index, schema or migration change: `count(*)` on the primary key table is enough at this size (non-goal: schema change).
- The route is a literal path `GET /todos/count` on the existing `/todos` router, declared directly after `GET /todos` and before the `/{todo_id}` routes. There is no `GET /todos/{todo_id}`, so nothing can shadow it. For `PATCH`/`DELETE /todos/count`, Starlette prefers a full match (path and method) over a partial match (path only), so the request reaches `patch_todo`/`delete_todo`, where `parse_id("count")` returns `None` and the existing `404 todo_not_found` is raised (AC-900.2). The id routes and their order of checks stay unchanged.
- No ADR: the decision is local to this endpoint.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/repository.py` | `count_todos(conn) -> int` | changed |
| `src/todo_api/todos/router.py` | `GET /todos/count` handler | changed |
| `README.md` | endpoint list | changed |

## Contract

`GET /todos/count` (no query parameters, no body; any query string is ignored)

- `200`, `Content-Type: application/json`, body `{"count": <int>}`: the number of todos that exist at the time of the query, a non-negative JSON integer (not a string, not a float). Three todos give `{"count": 3}` (AC-900.1); none (including a never-used database) gives `{"count": 0}` (AC-900.2). The body has no other key.
- `503` `{"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` when the database cannot be reached within the existing deadline, exactly as for `GET /todos`.

Unchanged id routes for the literal segment `count` (AC-900.2), the same as any other unknown id:

- `PATCH /todos/count` with a valid body such as `{"done": true}` → `404` `{"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}`. An invalid body keeps answering `422` first, as for any id (existing rule order: body before id).
- `DELETE /todos/count` → `404` with the same `todo_not_found` body.

Other methods on `/todos/count` (`POST`, `PUT`) keep the existing generic `405` `method_not_allowed` answer. `GET /todos`, `POST /todos`, `PATCH /todos/{id}` and `DELETE /todos/{id}` do not change.

## Data

No change. Query: `SELECT count(*) FROM todos`, no parameters.

## Risks

- A future `GET /todos/{todo_id}` must be declared after `GET /todos/count`, or `count` would be parsed as an id. The handler's docstring says so.
