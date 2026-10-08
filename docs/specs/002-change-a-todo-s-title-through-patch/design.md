# Design — 002 Change a todo's title through PATCH /todos/{id}

Builds on [001's design](../001-todo-rest-api-list-create-mark-done-not/design.md). Everything there stays valid. The only changes are the ones listed here.

## Decisions

- **Extend `PATCH /todos/{id}` and do not add a route.** `parse_patch` now returns a small value object, `PatchRequest(title: str | None, done: bool | None)`, where `None` means "not in the request". One repository function, `update_todo`, writes whichever fields are set. Then a done-only body, a title-only body and a combined body all take one code path and one SQL statement (AC-002.1, AC-002.3, AC-002.11).
- **One title helper shared by POST and PATCH.** `_parse_title(value: object) -> str` in `validation.py` runs the title rules in this order: `null` → `title_required`, not a string → `invalid_request`, then `str.strip()`, empty → `title_required`, more than 200 code points → `title_too_long`. `parse_create` passes `data.get("title")` to it, so a missing key is still `title_required` and POST behaviour is unchanged. `parse_patch` calls it only when the `title` key is present (AC-002.4 to AC-002.8).
- **A single `UPDATE` with `COALESCE`.** No read-then-write. A title-only update never overwrites a concurrent `done` change, and the reverse also holds. Under READ COMMITTED, Postgres re-evaluates `COALESCE(NULL, done)` against the newest row version after it waits on the row lock (AC-002.12). `created_at` and `id` do not appear in the `SET` clause (AC-002.1, AC-002.2). The explicit casts `%s::text` / `%s::boolean` keep the parameter types fixed when the value is `NULL`.
- **No migration and no `updated_at`.** The existing `CHECK (char_length(title) BETWEEN 1 AND 200)` already guards edited titles.
- **An operation that misses its deadline never commits.** This is a change to `Database`. In 001, an abandoned operation could still commit after a paused database resumed (001 design, Risks). This spec's contract says a 503 "writes nothing", and AC-002.13 requires the previous title after recovery. So `Database.run` fixes a deadline when it starts. If `op(conn)` returns after that deadline, `_guarded` rolls back instead of committing. This applies to every write (POST and DELETE included), which only makes 001's behaviour stricter. No 001 test depends on the old behaviour.
- **Concurrency is last-write-wins.** `If-Match` and other precondition headers are ignored, and there is no 409 or 412 (AC-002.12). FastAPI does not act on `If-Match`, so no code is needed. The task only must not add any such check.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/todos/validation.py` | `PatchRequest`; shared `_parse_title`; `parse_create` reuses it; `parse_patch` returns `PatchRequest` and applies the PATCH rule order below | changed |
| `src/todo_api/todos/repository.py` | `update_todo(conn, todo_id, *, title, done) -> Todo \| None` replaces `set_done` | changed |
| `src/todo_api/todos/router.py` | `patch_todo` passes `PatchRequest` to `update_todo`; rule order unchanged (body, then id, then database) | changed |
| `src/todo_api/db.py` | rollback instead of commit when `op` finishes after the deadline | changed |
| `tests/unit/test_validation.py` | unit tests (not acceptance tests): `parse_patch` now returns `PatchRequest`; new title cases | changed |
| `README.md` | the PATCH endpoint line mentions `title` | changed |

Key signatures (types only):

```python
# todos/validation.py
@dataclass(frozen=True)
class PatchRequest:
    title: str | None  # stripped, 1..200 code points; None = not in the request
    done: bool | None  # None = not in the request
    # invariant: at least one is not None


def parse_create(raw: bytes) -> str: ...  # unchanged behaviour
def parse_patch(raw: bytes) -> PatchRequest: ...


# todos/repository.py
async def update_todo(
    conn: AsyncConnection, todo_id: UUID, *, title: str | None, done: bool | None
) -> Todo | None: ...  # None = not found
```

SQL of `update_todo` (bound parameters only):

```sql
UPDATE todos
   SET title = COALESCE(%s::text, title),
       done  = COALESCE(%s::boolean, done)
 WHERE id = %s
RETURNING id, title, done, created_at
```

## Contract

The spec's contract (Product context → Contract) is binding. This section fixes the details it leaves open. Testers write against both. `GET`, `POST`, `DELETE`, the probes, serialization and the error body format are unchanged from 001's design.

### `PATCH /todos/{id}`: rule order (first failing rule wins)

"Present" means the key is in the JSON object, whatever its value (`null` counts as present). The request body is read as bytes and parsed as JSON regardless of `Content-Type`. An empty body is not valid JSON.

| # | Condition | Response | Criteria |
|---|---|---|---|
| 1 | body is not valid JSON, or not a JSON object | `422 invalid_request` | AC-002.10, AC-001.11 |
| 2 | neither `title` nor `done` present (`{}`, `{"foo": 1}`) | `422 invalid_request` | AC-002.10, AC-001.11 |
| 3 | `done` present and not a JSON boolean (`"true"`, `1`, `null`) | `422 invalid_request` | AC-002.10, AC-002.11 |
| 4 | `title` present and `null` | `422 title_required` | AC-002.5 |
| 5 | `title` present and not a string (`42`, `true`, `["x"]`, `{}`) | `422 invalid_request` | AC-002.8 |
| 6 | `title.strip()` is `""` | `422 title_required` | AC-002.5 |
| 7 | `len(title.strip()) > 200` (code points, no normalization) | `422 title_too_long` | AC-002.6 |
| 8 | `{id}` not a UUID (no database access) | `404 todo_not_found` | AC-002.9 |
| 9 | `UPDATE ... RETURNING` finds no row | `404 todo_not_found` | AC-002.9 |
| — | database unreachable or slower than 2.5 s | `503 unavailable` | AC-002.13 |
| 10 | otherwise | `200` updated Todo | AC-002.1 to AC-002.4, AC-002.7, AC-002.12 |

- Rules 1 to 7 need no database. They answer even while the database is down, and for unknown, deleted or non-UUID ids (AC-002.10). Rule 8 also answers without the database. So the acceptance tests for AC-002.13 must use UUID ids.
- Messages: `title_required` → `Title is required`, `title_too_long` → `Title must be at most 200 characters`, `todo_not_found` → `This todo no longer exists`, `unavailable` → `Todos are unavailable, please try again`. `invalid_request` keeps 001's non-empty message.
- `200` body: exactly `id`, `title` (stored, stripped), `done`, `created_at` in 001's serialization. `created_at` and `id` equal their values before the request. Fields that are not in the request keep their stored value. Sending the current value is a `200` no-op.
- Keys other than `title` and `done` are ignored, including `id`, `created_at` and `updated_at`.
- A 422, 404 or 503 writes nothing. A 503 caused by the deadline also writes nothing (see Decisions).
- A done-only body (with or without unknown keys) gives exactly 001's results: same statuses, codes and bodies, and the title is untouched (AC-002.11).

### Test harness

No new fixtures. The acceptance tests for this spec go in a new file (e.g. `tests/test_todos_title_patch.py`) and reuse `tests/conftest.py` as it is: `client`, `postgres_url`, `running(url)` for the restart in AC-002.1, and `container_url` with `pause()`/`unpause()` for AC-002.13. In the AC-002.13 test, pause after the todo exists, send the title PATCH with a UUID id (expect 503 within 3 s), unpause, wait for `/ready` 200, then check the old title. `tests/test_todos_api.py` (spec 001) is not modified.

## Data

No change. Table `todos` and its CHECK and index stay as in 001. No migration.

## Risks

- **A commit sent just before the deadline.** If `COMMIT` reaches the socket before the deadline and the database stalls before answering, the commit can still land after the 503. The window is the commit round trip only. It is accepted, as in the product contract's timeout note: todo-web never shows such a save as successful, and a reload shows the true state.
- **Unit test change.** `tests/unit/test_validation.py::test_parse_patch_accepts` asserts the old `bool` return and is updated in t3. It is a unit test of an internal function, not an acceptance test, so the rule "no spec 001 regression test changes" still holds: `tests/test_todos_api.py` is untouched.
