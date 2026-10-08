# Verification — 001 Todo REST API (list, create, mark done/not done, delete) persisted in Postgres

**Result:** pass
**Commit:** 025d938 · **Base:** 5e3e31f · **Trace:** 18/18 criteria named by tests (`tests/test_todos_api.py`, missing: none)

Test run (Phase 3): `devbox run test` 94 passed, 0 failed, 97 % coverage; `devbox run quality` passes. The acceptance tests in `tests/test_todos_api.py` and the harness in `tests/conftest.py` have changed only in formatting since the red commit 7979bed (b5564d1: import order and line wrapping, no changed assertions).

All test ids below are in `tests/test_todos_api.py`; all source paths are under `src/todo_api/`.

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-001.1 | met | `test_list_empty_returns_empty_array` | `todos/router.py:34-37`, `todos/repository.py:32-35` | Asserts `200` and `[]`. |
| AC-001.2 | met | `test_list_three_ordered_with_exact_fields` | `todos/repository.py:34` (`ORDER BY created_at, id`), `todos/router.py:19-27` (exactly four keys) | Asserts the four keys, creation order, and `(created_at, id)` sorted. Equal `created_at` cannot be produced reliably over HTTP, so the id tie-break is proven by the SQL and the sorted-keys assertion, not by a forced tie. |
| AC-001.3 | met | `test_create_returns_todo` | `todos/router.py:40-48`, `todos/repository.py:38-47` (`uuid.uuid4()` at :42, PK at :15), `todos/router.py:20-21` (`…mmmZ`) | Asserts `201`, UUID v4 in canonical form, id differs from the other todo, `title`, `done is False`, RFC 3339 `.mmmZ` regex, and that the todo is last in `GET /todos`. Uniqueness across all todos rests on the primary key. |
| AC-001.4 | met | `test_create_trims_whitespace_keeps_inner` | `todos/validation.py:36` (`str.strip()`) | Asserts `"  Buy milk\t\n"` becomes `"Buy milk"` in the response and in `GET /todos`, and that `"Buy  milk"` is kept as sent. |
| AC-001.5 | met | `test_create_title_required` (missing, `null`, `""`, `"   "`, `" \t\n "`) | `todos/validation.py:31-33`, `:37-38`; `errors.py:13` | `assert_error` checks status, JSON content type, the exact body shape, code and message; `GET /todos == []` afterwards. |
| AC-001.6 | met | `test_create_title_too_long` (201 × `a`, 201 × `é`), `test_create_title_too_long_after_trim_boundary` | `todos/validation.py:39-40` (`len` in code points); `errors.py:14` | Exact code and message; nothing created. |
| AC-001.7 | met | `test_create_title_exactly_200` (200 × `a`, 200 × `é`, 200 × `a` with spaces around) | `todos/validation.py:39` (`> 200`), DB guard `todos/repository.py:16` | Asserts `201` and 200 code points in the response and in `GET /todos`. |
| AC-001.8 | met | `test_create_invalid_request` (invalid JSON, empty body, `[]`, `"x"`, `42`, `{"title": 42/true/["x"]}`), `test_create_ignores_other_fields` | `todos/validation.py:18-25`, `:34-35`; extra keys ignored at `:31` | Asserts code `invalid_request`, a non-empty message, and that nothing is created. Extra fields (`done`, `id`, `created_at`, `extra`) are ignored and the todo is created with server values. |
| AC-001.9 | met | `test_patch_mark_done` | `todos/router.py:51-64`, `todos/repository.py:50-56` | Response equals the original todo with `done: true` (so `id`, `title` and `created_at` are unchanged); `GET /todos` agrees; repeating the request returns `200` with `done: true`. |
| AC-001.10 | met | `test_patch_mark_not_done` | same as AC-001.9 | Response and `GET /todos` equal the original with `done: false`; repeating returns `200`. |
| AC-001.11 | met | `test_patch_invalid_request` (`[]`, `"x"`, invalid JSON, empty, `{}`, `"true"`, `1`, `null`) | `todos/validation.py:44-50` (`isinstance(done, bool)`); body parsed before the id and before any DB access, `todos/router.py:53` | Asserts `422 invalid_request` and that the todo is unchanged in `GET /todos`. |
| AC-001.12 | met | `test_delete_removes_only_that_todo` | `todos/router.py:67-78`, `todos/repository.py:59-61` | Asserts `204`, an empty body, and that the other two todos are unchanged and still in order. |
| AC-001.13 | met | `test_unknown_id_is_404_without_side_effects` (random UUID, deleted id, `abc`; PATCH with a valid body and DELETE) | `todos/validation.py:53-58`; `todos/router.py:54-56`, `:62-63`, `:69-71`, `:76-77`; `errors.py:16` | Exact code and message for all six cases; the remaining list is unchanged. |
| AC-001.14 | met | `test_shared_list_without_credentials` | No auth dependency anywhere: `main.py:38-75`, `todos/router.py:16` | A second app instance gets the same list with odd headers and cookies and with no extra headers. GET and POST are not 401/403; PATCH and DELETE succeed without credentials in AC-001.9, AC-001.10 and AC-001.12. |
| AC-001.15 | met | `test_fresh_database_starts_and_keeps_todos` | `main.py:40-43` (lifespan opens the DB), `db.py:60-77` (`ensure_schema` under `pg_advisory_xact_lock`), `todos/repository.py:13-21` (`IF NOT EXISTS`) | Drops the table, starts the app, then asserts `/ready` is `ready` and `GET /todos` is `200 []`. A second start against the same DB keeps the todo. |
| AC-001.16 | met | `test_restart_keeps_todos_ids_and_order` | Persistence via `db.py:79-85` (commit at :84) | Mixed done states; after a fresh app instance the full JSON list (id, title, done, created_at, order) equals the list from before the restart. The design (Test harness) accepts a new app instance as the "new process". |
| AC-001.17 | met | `test_unreachable_database_refused` (port 1), `test_unreachable_database_hanging` (paused container) | `db.py:87-99` (2.5 s `asyncio.wait`, connection errors become `DatabaseUnavailable`), `db.py:55-56` (pool timeout 2 s, `connect_timeout` 2), `errors.py:51-53`, `main.py:52-61` | GET, POST, PATCH and DELETE (valid bodies, UUID ids) each return `503` with the exact body in under 3 s. `/ready` returns `503` in under 3 s. `/health` returns `200 {"status": "ok"}`. Both connection-refused and hanging connections are covered. |
| AC-001.18 | met | `test_recovery_without_restart` | `db.py:57` (`check_connection` on checkout), `db.py:80-81` (lazy schema), `main.py:57-61` | Same app instance: pause gives `503` on `/ready` and `/todos`; after unpause `/ready` returns `200 {"status": "ready"}` (polled for up to 15 s; the criterion sets no time bound) and `/todos` returns the stored todo. |

### Observations (not failures)

- The AC-001.17 tests do not assert the `Content-Type` header or the `/ready` 503 body. The criterion only requires `503` for `/ready`, and every error goes through `JSONResponse` in `errors.py:41-42`, so the header is set.
- A title containing a NUL character (`\u0000`) passes validation, but Postgres `text` rejects it. psycopg raises `DataError`, which is not a connection error (`db.py:26-31`), so the request returns `500 internal_error` instead of a 4xx. No criterion covers this. Suggested follow-up through `/svc:fix-bug` or a spec amendment.
- `tests/conftest.py:103-105` defines a `second_client` fixture that nothing uses. This is harmless.

## Non-goals

None of the excluded features were built:
- Authentication or users: none.
- Fields beyond the four: none.
- Title editing: PATCH only accepts `done` (`todos/validation.py:44-50`).
- `GET /todos/{id}`: not added; that route answers `405 method_not_allowed`.
- Paging, filtering, search, or a limit on the number of todos: none.
- Exposure, DB provisioning, or promotion: no gitops, Dockerfile or CI changes. ✔

## Deviations from the plan

All six tasks are `done: true`. These files changed but are in no task's `files`:

- `docs/adr/001-postgres-persistence.md`: the ADR that `design.md` and `plan.md` link to (architect output). Acceptable.
- `docs/security/scan-2026-10-08.md`: output of the security phase. Acceptable.
- `docs/specs/001-…/{spec,design,plan}.md`: spec workflow artifacts. The `design.md` change in 6598a4e is formatting only and changes no contract. Acceptable.
- `tests/conftest.py`, `tests/test_todos_api.py`: owned by the tester per the plan, outside the tasks. After the red commit they changed only in formatting (b5564d1). Acceptable.
- `src/todo_api/tracing.py`, `tests/test_tracing.py`: formatting only (b5564d1), approved by the user. No behaviour change. Acceptable.
- `tests/unit/test_errors.py`, `tests/unit/test_db_internals.py`: unit tests beyond the parser tests that t2 allows under `tests/unit/`. They are not acceptance tests and contain no criterion ids. Acceptable.
- History: commit 3c71499 (`wip: interrupted task`) holds t2's files, and t2 was completed in d819c20 and merged. This is history noise only; squashing it at merge is recommended. Acceptable.

## Contract

Matches `design.md` and the spec's contract:
- Rule order: POST in `todos/validation.py:28-41`; PATCH checks the body, then the id, at `todos/router.py:53-56`; no DB access before validation.
- Error body is exactly `{"error": {code, message}}` (`errors.py:41-42`). The default `RequestValidationError` body is replaced (`errors.py:56-57`), and `404 not_found`, `405 method_not_allowed` and `500 internal_error` are in place (`errors.py:19-22`, `:67-70`).
- Serialization: lowercase UUID and `YYYY-MM-DDTHH:MM:SS.mmmZ` in UTC (`todos/router.py:19-27`).
- DDL is identical to the design's Data section (`todos/repository.py:13-21`).
- Pool settings, the 2.5 s deadline and the background-task handling match t4 (`db.py:16`, `:23-40`, `:50-58`, `:87-99`).
- `create_app(database_url=None)` resolves `DATABASE_URL` in the lifespan, not at import (`main.py:31-47`).
- `/health` does not touch the DB. `/ready` uses `db.ping()` (`main.py:52-61`).
- `DATABASE_URL` and `TEST_DATABASE_URL` are documented in `docs/env-vars.md`.
- `uv.lock` contains `psycopg`, `psycopg-binary`, `psycopg-pool` and `testcontainers`.

The `invalid_request` message is fixed (`Request body is invalid`, `errors.py:15`), which the contract allows ("free text"). ✔
