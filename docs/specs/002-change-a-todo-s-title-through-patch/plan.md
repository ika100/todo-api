---
spec_id: 002-change-a-todo-s-title-through-patch
shape: service-python
spec_hash: 73b5f6f1ea1c
summary: Extend PATCH /todos/{id} to change the title (shared title rules with create, one UPDATE, last write wins) and never
  commit an operation that missed its deadline
tasks:
- id: t1
  title: Add repository.update_todo (title and/or done in one UPDATE)
  files: [src/todo_api/todos/repository.py]
  covers: [AC-002.1, AC-002.2, AC-002.3, AC-002.4, AC-002.7, AC-002.12]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Roll back instead of committing when an operation misses its deadline
  files: [src/todo_api/db.py]
  covers: [AC-002.13]
  parallel_safe: true
  depends_on: []
  done: true
- id: t3
  title: Parse title in PATCH with the shared title rules and wire patch_todo to update_todo
  files: [src/todo_api/todos/validation.py, src/todo_api/todos/router.py, src/todo_api/todos/repository.py, tests/unit/test_validation.py,
    README.md]
  covers: [AC-002.1, AC-002.2, AC-002.3, AC-002.4, AC-002.5, AC-002.6, AC-002.7, AC-002.8, AC-002.9, AC-002.10, AC-002.11,
    AC-002.12, AC-002.13]
  parallel_safe: true
  depends_on: [t1]
---

# Plan — 002 Change a todo's title through PATCH /todos/{id}

Design and the binding rule order: [design.md](design.md). There is no ADR: every decision is local to this feature.

Levels: t1, t2 → t3. The acceptance tests for this spec are written by the testers in a new file before coding, using the existing `tests/conftest.py` harness (see design, "Test harness"). No task edits them. No task touches `tests/test_todos_api.py` (spec 001). There is no migration, and `pyproject.toml`, `Dockerfile`, CI and `docs/env-vars.md` do not change.

## t1 — Add repository.update_todo (title and/or done in one UPDATE)

**Files:** src/todo_api/todos/repository.py
**Covers:** AC-002.1, AC-002.2, AC-002.3, AC-002.4, AC-002.7, AC-002.12
**Goal:** one parameterized statement that changes the title, the done state or both, never touches `id` or `created_at`, and keeps any field that is not given.

**Implementation notes:**
- Add `async def update_todo(conn, todo_id: UUID, *, title: str | None, done: bool | None) -> Todo | None`. `None` for a field means "keep it".
- SQL: exactly the statement in the design (`COALESCE(%s::text, title)`, `COALESCE(%s::boolean, done)`, `RETURNING id, title, done, created_at`), with `class_row(Todo)` like the other queries.
- Keep `set_done` for now so that `router.py` keeps working on this branch. t3 removes it.
- Bound parameters only (bandit clean). Do not change `SCHEMA_SQL`.

**Done when:** `devbox run quality` and `devbox run bandit` pass and all existing tests pass. The AC-002 acceptance tests pass after t3.

## t2 — Roll back instead of committing when an operation misses its deadline

**Files:** src/todo_api/db.py
**Covers:** AC-002.13
**Goal:** a request that answered `503` because of the 2.5 s deadline never writes later, after the database resumes.

**Implementation notes:**
- In `run`, compute `deadline = loop.time() + OP_DEADLINE_S` before scheduling the task, and pass it to `_guarded`.
- In `_guarded`, after `op(conn)` returns, check the deadline. If `loop.time() >= deadline`, call `await conn.rollback()` and raise an internal `_DeadlineMissed` exception (module-private) instead of committing.
- `_DeadlineMissed` only occurs in abandoned tasks. `_consume` logs it like other abandoned failures (`database_abandoned_operation_failed`). Never log the URL.
- Leave the 2.5 s deadline, the pool settings, the error mapping and the `ensure_schema` path unchanged.

**Done when:** `devbox run quality` passes and the spec 001 acceptance tests (AC-001.17 and AC-001.18 included) still pass. The AC-002.13 acceptance test passes after t3.

## t3 — Parse title in PATCH with the shared title rules and wire patch_todo to update_todo

**Files:** src/todo_api/todos/validation.py, src/todo_api/todos/router.py, src/todo_api/todos/repository.py, tests/unit/test_validation.py, README.md
**Covers:** AC-002.1 to AC-002.13
**Goal:** `PATCH /todos/{id}` accepts `title`, `done` or both with the design's rule order. A done-only body behaves exactly as in spec 001.

**Implementation notes:**
- `validation.py`: add the frozen dataclass `PatchRequest(title: str | None, done: bool | None)` and a private `_parse_title(value: object) -> str` (rules: `None` → `title_required`, not `str` → `invalid_request`, strip, empty → `title_required`, `> MAX_TITLE_LENGTH` → `title_too_long`). `parse_create` becomes `_load_object` followed by `_parse_title(data.get("title"))`, with identical behaviour.
- `parse_patch(raw) -> PatchRequest`: `_load_object`. If neither key is present → `invalid_request`. If `"done" in data` and `not isinstance(data["done"], bool)` → `invalid_request`. Then, if `"title" in data` → `_parse_title(data["title"])`. Keep this exact order (design rules 1 to 7).
- `router.patch_todo`: `req = parse_patch(body)`, then `parse_id` (non-UUID → 404), then `db.run` with `repository.update_todo(conn, parsed, title=req.title, done=req.done)`. `None` → `404 todo_not_found`. Do not read or act on `If-Match` or other precondition headers.
- `repository.py`: delete `set_done`, which is no longer used.
- `tests/unit/test_validation.py`: change `test_parse_patch_accepts` to expect `PatchRequest(title=None, done=True/False)`. Add unit cases for title-only, combined, stripped, 200 and 201 code points, `{"done": "x", "title": null}` → `invalid_request` and `{"title": null, "done": true}` → `title_required`. Keep every existing reject case.
- `README.md`: the PATCH line becomes "change a todo's title and/or done state (`{"title": "..."}`, `{"done": true|false}`)", and add a link to spec 002 next to the spec 001 link.

**Done when:** every AC-002.1 to AC-002.13 acceptance test and the whole unchanged `tests/test_todos_api.py` pass with `devbox run test`, and `devbox run quality` and `devbox run security` pass.
