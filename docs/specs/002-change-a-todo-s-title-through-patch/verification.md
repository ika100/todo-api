# Verification — 002 Change a todo's title through PATCH /todos/{id}

**Result:** pass
**Commit:** f39a7eb · **Base:** 363a6a2 · **Trace:** 13/13 criteria named by tests (`tests/test_todos_title_patch.py`)

Test run (Phase 3): `devbox run test` 158 passed, 0 failed, 97% coverage; quality and security PASS.
Acceptance tests were committed red in `8d05921`; the only later change (`737becd`) is ruff formatting of two calls in `test_rule_order_on_existing_todo` and `test_last_write_wins_no_conflict` (same assertions, same ids). `tests/test_todos_api.py` (spec 001) is untouched.

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-002.1 | met | `tests/test_todos_title_patch.py::test_title_change_persists_across_restart` | `src/todo_api/todos/router.py:59`, `src/todo_api/todos/repository.py:50-61` | The test asserts the whole body equals the original with the new title (so `id`, `done`, `created_at` are unchanged), checks `set(body) == {id,title,done,created_at}`, then `GET` and `GET` again from a second app via `running(postgres_url)`. |
| AC-002.2 | met | `::test_title_change_keeps_order_and_done` | `src/todo_api/todos/repository.py:56-58` (SET touches only `title`/`done`) | Checks the order of the ids, that the middle todo keeps `done` true and `created_at`, and that the neighbours are unchanged. |
| AC-002.3 | met | `::test_title_and_done_together_and_same_title` | `src/todo_api/todos/validation.py:53-64`, `repository.py:56-58` | Combined body gives 200 and is persisted. Sending the same title again gives 200 with the todo unchanged. |
| AC-002.4 | met | `::test_title_is_trimmed_inner_spaces_kept` | `src/todo_api/todos/validation.py:40` (`str.strip()`) | Covers `"  Buy oat milk\t\n"` and inner double space, in both the response and `GET`. |
| AC-002.5 | met | `::test_title_required` (null, "", "   ", with and without `done`) | `src/todo_api/todos/validation.py:36-37, 41-42` | Checks the exact code and message, and that `GET` equals the original todo (title and done unchanged). |
| AC-002.6 | met | `::test_title_too_long` (201 × a / é, ± done), `::test_title_too_long_after_trim_boundary` | `src/todo_api/todos/validation.py:43-44` | Exact code and message; todo unchanged. |
| AC-002.7 | met | `::test_title_exactly_200` (200 × a, 200 × é, padded) | `src/todo_api/todos/validation.py:43` (`>` not `>=`) | Asserts 200 code points both in the response and in the stored value. |
| AC-002.8 | met | `::test_title_not_a_string` (42, true, ["x"], {}) | `src/todo_api/todos/validation.py:38-39` | `invalid_request` with a non-empty message; todo unchanged. |
| AC-002.9 | met | `::test_unknown_ids_are_404_without_side_effects` | `src/todo_api/todos/router.py:54-56, 62-63` | Random UUID, deleted id and `abc` each give 404 `todo_not_found` with the exact message. The list is unchanged afterwards (nothing created). |
| AC-002.10 | met | `::test_rule_order_before_id_lookup` (10 bodies × unknown/deleted/abc), `::test_rule_order_on_existing_todo` | `src/todo_api/todos/router.py:53` (body parsed before `parse_id`), `src/todo_api/todos/validation.py:57-64` | Tests every step of the order, including `{"done":"x","title":null}` → `invalid_request` and the "422 not 404" rule. The order in the code matches design rules 1 to 7. |
| AC-002.11 | met | `::test_done_only_unchanged_title`; spec 001 suite `tests/test_todos_api.py` unchanged and passing | `src/todo_api/todos/validation.py:57-62`, `repository.py:56` (`COALESCE(NULL, title)`) | Done-only bodies, with or without extra keys, keep the title. 404 on unknown and invalid ids. The spec 001 PATCH criteria are still covered by the unmodified 001 tests. |
| AC-002.12 | met | `::test_last_write_wins_no_conflict` (with `If-Match`), `::test_title_patch_keeps_other_callers_done` | `src/todo_api/todos/router.py:51-64` (no precondition handling), `repository.py:56-58` (single COALESCE UPDATE) | Sequential calls from two callers, which is what the criterion describes ("one after the other"). A second app instance sets `done`, and a title-only PATCH keeps it. |
| AC-002.13 | met | `::test_unreachable_database_title_patch` | `src/todo_api/db.py:95-102` (2.5 s deadline → `DatabaseUnavailable`), `src/todo_api/db.py:88-90` (rollback instead of commit after the deadline) | Pauses Postgres, asserts 503 `unavailable` with the exact message in under 3 s, unpauses, waits for `/ready`, and asserts the previous title. Uses a UUID id, as the design requires. |

## Non-goals

- No new route: only `PATCH /{todo_id}` is extended (`router.py:51`). ✔
- No `updated_at`, no history; `created_at` and `id` are not in the SET clause (`repository.py:56-58`). `grep updated_at src/` finds nothing. ✔
- No optimistic concurrency: there are no `If-Match` or ETag references in `src/`, and no 409 or 412 path. ✔
- No other fields changed, no reordering, no schema change (`SCHEMA_SQL` untouched), no migration. ✔
- GET, POST and DELETE are behaviourally unchanged. `parse_create` now delegates to the shared `_parse_title` with identical rules (`validation.py:48-50`), and the 001 tests pass unchanged. The `db.py` deadline rollback applies to every write. The design explicitly accepts this as a stricter 001 behaviour, not a feature excluded by the spec. ✔
- Probes, configuration, Dockerfile, deployment: unchanged. ✔

## Deviations from the plan

- `docs/security/scan-2026-10-08.md` changed but is in no task's `files`. It is the security phase's report, overwritten for this run. Acceptable. Note that it drops the earlier detailed list of trivy base-image HIGH findings and keeps only a summary sentence. That history is still in git.
- `tests/test_todos_title_patch.py` changed after the red commit (`737becd`), but only ruff formatting (line wrapping), with no change to assertions or criterion ids. Acceptable under the testing rules (lint-fix formatting).
- Every task (t1, t2, t3) has `done: true`. `set_done` was removed as planned in t3 (no references remain in `src/`). Exception class named `_DeadlineMissedError` instead of `_DeadlineMissed` (ruff naming). Acceptable.

## Contract

The implementation matches `design.md`: `PatchRequest(title, done)` (`validation.py:15-18`), `_parse_title` shared by POST and PATCH, PATCH rule order 1 to 9 (body before id, non-UUID gives 404 without database access), the exact `COALESCE(%s::text, title)` / `COALESCE(%s::boolean, done)` UPDATE with `RETURNING id, title, done, created_at`, and the rollback-after-deadline in `Database._guarded`. The error codes and messages are those in the contract table. ✔

## Observations (non-blocking)

- `src/todo_api/db.py:95-107` has a narrow race. The deadline is computed just before `asyncio.wait(timeout=OP_DEADLINE_S)`. If `op` finishes between `deadline` and the end of the wait (microseconds), the task completes with `_DeadlineMissedError`. That error is not in `_CONNECTION_ERRORS`, so it would surface as a 500 through the generic handler instead of a 503. Nothing is written in that case, so the spec's "writes nothing" holds. Suggested follow-up: add `_DeadlineMissedError` to the mapped errors in `run`. This does not affect any criterion's tested outcome. **Fixed after review in `ec49ece`:** `run` now maps `_DeadlineMissedError` to `DatabaseUnavailable` (503); unit test `test_deadline_missed_at_boundary_maps_to_unavailable`.
