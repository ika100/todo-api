---
spec_id: 002-change-a-todo-s-title-through-patch
title: Change a todo's title through PATCH /todos/{id}, with the same validation and trimming as create
status: approved
priority: P1
shape: service-python
parent: ika100/todo:002-update-a-notice
---

# 002 — Change a todo's title through PATCH /todos/{id}, with the same validation and trimming as create

## Problem

The todo list (spec 001) lets a user add, tick off and delete todos, but a todo's title can't be changed after it is added. To fix a typo or make a task more precise ("Buy milk" to "Buy oat milk"), the user has to delete the todo and add it again. That loses its place in the list, because the list is ordered oldest first, and it loses its done state. Spec 001 left title editing out on purpose; this spec adds it.

## Product context

Slice of the product plan `002-update-a-notice` in `ika100/todo` for `todo-api` (service-python). The product criteria and the contract below are binding: every criterion of this spec implements one of them and names it: `(product AC-<NNN>.<n>)`.

### Product criteria

- **AC-002.2** Given a todo "Buy milk" in edit mode, when the user changes the title to "Buy oat milk" and saves (with the Enter key or a "Save" control), then the todo is shown in place in the list as "Buy oat milk" without a full page reload, and it is still shown as "Buy oat milk" after the page is reloaded.
- **AC-002.3** Given a todo whose title was changed, when the list is shown, then the todo keeps its done state and its position in the list (ordering by creation time is unaffected by the change).
- **AC-002.5** Given a todo in edit mode, when the user saves a title that is empty or only whitespace, then the title is not changed, the todo stays in edit mode and the page shows "Title is required".
- **AC-002.6** Given a todo in edit mode, when the user saves a title longer than 200 characters, then the title is not changed, the todo stays in edit mode and the page shows "Title must be at most 200 characters"; a title of exactly 200 characters is saved.
- **AC-002.7** Given a todo in edit mode, when the user saves a title with leading or trailing spaces, then the todo is stored and shown with those spaces removed.
- **AC-002.8** Given a todo that was deleted in another browser tab, when the user saves a new title for it in the current tab, then the page shows "This todo no longer exists" and the list is refreshed from todo-api.
- **AC-002.10** Given the same todo is edited in two browser tabs, when both save different titles one after the other, then the title saved last is the one shown after reloading either tab (last save wins, no conflict warning).

### Contract

Base URL inside the environment: `http://todo-api` (env `TODO_API_URL` on todo-web, already set). All bodies are
JSON (`Content-Type: application/json`, UTF-8). No authentication, no user scoping: one shared list. Everything in
spec 001's contract stays valid; this plan changes only `PATCH /todos/{id}`. The full contract is restated here so
each repo's spec is self-contained.

### Todo object (unchanged)

| Field | Type | Notes |
|---|---|---|
| `id` | string | UUID (v4), assigned by todo-api; never changes |
| `title` | string | trimmed, 1..200 Unicode code points; changeable with PATCH |
| `done` | boolean | `false` on creation; changeable with PATCH |
| `created_at` | string | RFC 3339 timestamp in UTC; set on creation, **never changed by PATCH** |

No new field (no `updated_at`).

### Endpoints

**`GET /todos`** (unchanged) — `200`, JSON array of Todo objects ordered by `created_at` ascending, then `id`
ascending. An edited todo keeps its position.

**`POST /todos`** (unchanged) — `{"title": "<string>"}` -> `201` Todo; `422` `title_required` / `title_too_long` /
`invalid_request` as in spec 001.

**`PATCH /todos/{id}`** (extended) — change the title, the done state, or both.

- Request: a JSON object with at least one of
  - `title`: string — the new title;
  - `done`: boolean — the new done state (spec 001 behaviour).
  Unknown fields are ignored. todo-web sends `{"title": "..."}` for an edit and `{"done": true|false}` for a toggle.
- Rules, applied in this order (the first failing rule answers):
  1. body is not a JSON object -> `422 invalid_request`;
  2. neither `title` nor `done` is present -> `422 invalid_request`;
  3. `done` is present and not a boolean -> `422 invalid_request`;
  4. `title` is present and `null` -> `422 title_required`;
  5. `title` is present and not a string -> `422 invalid_request`;
  6. `title` trimmed (leading and trailing Unicode whitespace, as Python `str.strip()`) is empty -> `422 title_required`;
  7. trimmed `title` longer than 200 code points -> `422 title_too_long` (exactly 200 is accepted);
  8. no todo with this id (including ids that are not valid UUIDs and deleted todos) -> `404 todo_not_found`.
- `200` — the updated Todo object, with the trimmed `title`. Fields not in the request keep their values;
  `created_at` and `id` never change. Setting a field to its current value is a no-op that still returns `200`.
- A failed request (422, 404, 503) writes nothing.
- Concurrency: no version or precondition check. Concurrent PATCHes are applied in commit order; the last one wins
  and no conflict status is ever returned.

**`DELETE /todos/{id}`** (unchanged) — `204`; `404 todo_not_found` for unknown, invalid or already deleted ids.

### Errors

Every 4xx/5xx response produced by todo-api has this body (unchanged from spec 001):

```json
{"error": {"code": "title_required", "message": "Title is required"}}
```

| HTTP | `code` | `message` | todo-web shows (edit save) |
|---|---|---|---|
| 422 | `title_required` | `Title is required` | "Title is required", stays in edit mode |
| 422 | `title_too_long` | `Title must be at most 200 characters` | "Title must be at most 200 characters", stays in edit mode |
| 422 | `invalid_request` | free text | "Todos are unavailable, please try again" (todo-web never sends such a body; treated as unexpected) |
| 404 | `todo_not_found` | `This todo no longer exists` | "This todo no longer exists", leaves edit mode, re-fetches the list |
| 503 | `unavailable` | `Todos are unavailable, please try again` | "Todos are unavailable, please try again" |

todo-web branches on HTTP status and `code`, never on `message`. Any response the contract does not list (another
status, a 4xx without the error body, a 2xx without a valid Todo) is treated like a 5xx: "Todos are unavailable,
please try again", and the title is not shown as saved.

### Timeouts

- todo-web -> todo-api, every call (including the new title PATCH and the list re-fetch after a 404): 5 s. No
  answer within 5 s, a connection error or any 5xx is "unavailable" (well under the 10 s of AC-002.9). No retries:
  the user retries by saving again.
- todo-api -> Postgres: the existing per-operation deadline; when the database is unreachable or slow, todo-api
  answers `503 unavailable` and writes nothing.
- If the 5 s timeout fires on todo-web while todo-api still commits the update, a later reload may show the new
  title; the web never claims it was saved. This is accepted (AC-002.9 only covers todo-api being unreachable).

### Configuration

No change: todo-web keeps `TODO_API_URL=http://todo-api`; todo-api keeps `DATABASE_URL` from the postgres addon. No
events: the only interaction is synchronous HTTP from todo-web to todo-api.

### Notes for this repo

Extend the existing PATCH /todos/{id} (src/todo_api/todos/validation.py parse_patch, router.patch_todo,
repository.set_done) instead of adding a new endpoint: the body may now carry `title`, `done`, or both.
Reuse the title rules of parse_create (one shared helper), keep the existing rule order (body validated before
the id lookup) and a done-only body must behave exactly as in spec 001 (no regression test may change).
Update title and/or done in one UPDATE statement; never touch `created_at` and do not add an `updated_at` column
(history is a non-goal). No schema migration is needed: the existing CHECK on `title` already covers 1..200.
Acceptance tests against a real Postgres, like spec 001.

## Stories

- As todo-web, I want to change a todo's title with `PATCH /todos/{id}`, so that a user can fix a typo or make a task more precise without deleting and re-adding it.
- As todo-web, I want a title change to apply the same trimming and the same error codes as creating a todo, so that the edit form shows the same messages ("Title is required", "Title must be at most 200 characters") as the add form.
- As todo-web, I want the existing done toggle (`{"done": ...}`) to keep working exactly as before, so that the spec 001 toggle and its tests stay untouched.
- As a user of the todo list page, I want an edited todo to keep its place in the list and its done state, so that editing a title changes nothing else.

## Acceptance criteria

All error bodies below have the contract's shape `{"error": {"code": "<code>", "message": "<message>"}}` with `Content-Type: application/json`. "The todo is unchanged" means a following `GET /todos` returns that todo with the same `title`, `done` and `created_at` as before the request, in the same position.

- **AC-002.1** Given a todo "Buy milk", when a caller sends `PATCH /todos/{id}` with `{"title": "Buy oat milk"}`, then the response is `200` with the todo whose `title` is `"Buy oat milk"`, whose `id`, `done` and `created_at` are unchanged, and which has exactly the fields `id`, `title`, `done` and `created_at` (no `updated_at`); a following `GET /todos` returns it with `title` `"Buy oat milk"`, also after todo-api is stopped and started again against the same database. (product AC-002.2)
- **AC-002.2** Given three todos created one after another, the middle one with `done` `true`, when a caller changes the middle todo's title with `PATCH /todos/{id}` `{"title": "..."}`, then a following `GET /todos` returns the three todos in the same order as before, the middle one still with `done` `true` and its original `created_at`, and the other two unchanged. (product AC-002.3)
- **AC-002.3** Given a todo "Buy milk" with `done` `false`, when a caller sends `PATCH /todos/{id}` with `{"title": "Buy oat milk", "done": true}`, then the response is `200` with `title` `"Buy oat milk"` and `done` `true`, and a following `GET /todos` shows both changes; sending a `title` equal to the current title answers `200` with the todo unchanged. (product AC-002.2)
- **AC-002.4** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a title that has leading or trailing Unicode whitespace such as `"  Buy oat milk\t\n"`, then the response is `200` with `title` `"Buy oat milk"` and `GET /todos` also returns `"Buy oat milk"`; inner spaces (`"Buy  oat milk"`) are kept as sent. (product AC-002.7)
- **AC-002.5** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a `title` that is `null`, `""` or whitespace only (e.g. `"   "`), alone or together with a valid `done` (e.g. `{"title": "  ", "done": true}`), then the response is `422` with code `title_required` and message `Title is required`, and the todo is unchanged (neither title nor done). (product AC-002.5)
- **AC-002.6** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a `title` that has more than 200 Unicode code points after trimming (e.g. 201 × `a`, or 201 × `é`), alone or together with a valid `done`, then the response is `422` with code `title_too_long` and message `Title must be at most 200 characters`, and the todo is unchanged. (product AC-002.6)
- **AC-002.7** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a `title` of exactly 200 code points after trimming (200 × `a`; 200 × `é`; 200 × `a` surrounded by spaces), then the response is `200` and the stored `title` has exactly 200 code points. (product AC-002.6)
- **AC-002.8** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a `title` that is not a string (e.g. `42`, `true`, `["x"]`, `{}`), then the response is `422` with code `invalid_request` and a non-empty `message`, and the todo is unchanged. (product AC-002.5)
- **AC-002.9** Given an id that belongs to no todo (a random UUID, an id that was already deleted, or a string that is not a UUID such as `abc`), when a caller sends `PATCH /todos/{id}` with a valid title body such as `{"title": "Buy oat milk"}`, then the response is `404` with code `todo_not_found` and message `This todo no longer exists`, and nothing is created or changed. (product AC-002.8)
- **AC-002.10** Given a `PATCH /todos/{id}` request that breaks more than one rule, when it is sent, then the first failing rule in this order answers: body not a JSON object (`invalid_request`); neither `title` nor `done` present, e.g. `{}` or `{"foo": 1}` (`invalid_request`); `done` present and not a boolean (`invalid_request`); `title` `null` (`title_required`); `title` not a string (`invalid_request`); `title` empty after trimming (`title_required`); `title` over 200 code points (`title_too_long`); unknown id (`404 todo_not_found`). In particular an unknown or deleted id with an invalid body answers `422`, not `404`, and `{"done": "x", "title": null}` answers `invalid_request`. (product AC-002.8)
- **AC-002.11** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a body carrying only `done` (with or without unknown extra fields), then every spec 001 criterion for `PATCH` (AC-001.9, AC-001.10, AC-001.11 for bodies without `title`, AC-001.13) still holds with the same status, code and body, and the todo's `title` is unchanged. (product AC-002.3)
- **AC-002.12** Given a todo, when one caller sends `PATCH /todos/{id}` `{"title": "A"}` and then another caller sends `{"title": "B"}` for the same todo, then both answer `200` (never `409` or `412`, also when an `If-Match` header is sent) and a following `GET /todos` returns `title` `"B"`; a title-only PATCH sent after another caller's `{"done": true}` leaves `done` `true`. (product AC-002.10)
- **AC-002.13** Given the database is unreachable, when a caller sends `PATCH /todos/{id}` with a valid title body, then todo-api answers `503` with code `unavailable` and message `Todos are unavailable, please try again` within 3 seconds; after the database is reachable again, `GET /todos` returns the todo with its previous title. (product AC-002.2)

## Non-goals

- A new endpoint for titles (e.g. `PUT /todos/{id}` or `/todos/{id}/title`): the existing `PATCH /todos/{id}` is extended.
- Edit history, an `updated_at` field, or any change to `created_at` on edit.
- Optimistic concurrency (versions, `ETag` / `If-Match`, conflict responses): the last write wins.
- Changing any field other than `title` and `done`; reordering todos.
- A schema change or data migration: the stored title rules (1..200) are unchanged.
- Any change to `GET /todos`, `POST /todos`, `DELETE /todos/{id}`, the probes, or the configuration.
- The edit UI (owned by todo-web), deployment changes and promotion to `staging` or `prod`.

## Open questions

None: the product spec and its contract decide every behaviour of this slice.

## Changelog

- 2026-10-08 created
- 2026-10-08 approved
