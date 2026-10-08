---
spec_id: 001-todo-rest-api-list-create-mark-done-not
title: Todo REST API (list, create, mark done/not done, delete) persisted in Postgres
status: draft
priority: P1
shape: service-python
parent: ika100/todo:001-todo-list
---

# 001 — Todo REST API (list, create, mark done/not done, delete) persisted in Postgres

## Problem

The todo product is deployed (todo-api and todo-web run in `dev`), but it does nothing a user can use yet: there is no page to open and nothing to keep track of. A user who wants to note tasks and tick them off has no way to do it. This spec delivers the first usable feature: one todo list in the browser, stored by todo-api, so that the deployed product does what its name says.

## Product context

Slice of the product plan `001-todo-list` in `ika100/todo` for `todo-api` (service-python). The product criteria and the contract below are binding: every criterion of this spec implements one of them and names it: `(product AC-<NNN>.<n>)`.

### Product criteria

- **AC-001.3** Given todos exist, when the user opens the todo list page, then every todo is shown with its title and its done state, ordered by creation time with the oldest first.
- **AC-001.5** Given the todo list page, when the user submits a title that is empty or only whitespace, then no todo is created and the page shows "Title is required".
- **AC-001.6** Given the todo list page, when the user submits a title longer than 200 characters, then no todo is created and the page shows "Title must be at most 200 characters"; a title of exactly 200 characters is accepted.
- **AC-001.7** Given a title with leading or trailing spaces, when the user adds it, then the todo is stored and shown with those spaces removed.
- **AC-001.8** Given a todo that is not done, when the user marks it as done, then it is shown as done, and it is still shown as done after the page is reloaded.
- **AC-001.9** Given a todo that is done, when the user marks it as not done, then it is shown as not done, and it is still shown as not done after the page is reloaded.
- **AC-001.10** Given a todo in the list, when the user deletes it, then it disappears from the list immediately, without a confirmation step, and does not reappear after the page is reloaded.
- **AC-001.11** Given a todo that was deleted in another browser tab, when the user marks it as done or deletes it in the current tab, then the page shows "This todo no longer exists" and the list is refreshed from todo-api.
- **AC-001.13** Given todos were added in one browser, when the same page is opened in a different browser, then the same list is shown (one shared list, no sign-in).
- **AC-001.14** Given todos exist, some done and some not done, when todo-api is restarted or redeployed in the `dev` environment, then after it is available again the todo list page shows the same todos with the same titles, done states and order; the todos are kept in the product's Postgres database provided by the postgres addon.

### Contract

Base URL inside the environment: `http://todo-api` (env `TODO_API_URL` on todo-web). All bodies are JSON
(`Content-Type: application/json`, UTF-8). No authentication, no user scoping: one shared list.

### Todo object

| Field | Type | Notes |
|---|---|---|
| `id` | string | UUID (v4), assigned by todo-api |
| `title` | string | trimmed, 1..200 Unicode code points |
| `done` | boolean | `false` on creation |
| `created_at` | string | RFC 3339 timestamp in UTC, e.g. `2026-10-08T12:34:56.789Z`; set by todo-api |

### Endpoints

**`GET /todos`** — list all todos.
- `200` — JSON array of Todo objects, ordered by `created_at` ascending, then `id` ascending. Empty list: `[]`.

**`POST /todos`** — create a todo.
- Request: `{"title": "<string>"}`. Unknown fields are ignored.
- todo-api trims leading and trailing whitespace (Unicode whitespace, as Python `str.strip()`), then validates.
- `201` — the created Todo object (`done: false`, trimmed `title`).
- `422` `title_required` — `title` missing, `null`, or empty after trimming.
- `422` `title_too_long` — more than 200 code points after trimming (exactly 200 is accepted).
- `422` `invalid_request` — body is not a JSON object or `title` is not a string.

**`PATCH /todos/{id}`** — set the done state.
- Request: `{"done": true}` or `{"done": false}`. Setting the current value again is a no-op that still returns `200`.
- `200` — the updated Todo object.
- `404` `todo_not_found` — no todo with this id (including ids that are not valid UUIDs).
- `422` `invalid_request` — body is not an object or `done` is missing / not a boolean.

**`DELETE /todos/{id}`** — delete a todo.
- `204` — deleted, empty body.
- `404` `todo_not_found` — no todo with this id (including ids that are not valid UUIDs, and ids already deleted).

### Error format

Every 4xx/5xx response produced by todo-api has this body (FastAPI's default validation body is replaced):

```json
{"error": {"code": "title_required", "message": "Title is required"}}
```

| HTTP | `code` | `message` |
|---|---|---|
| 422 | `title_required` | `Title is required` |
| 422 | `title_too_long` | `Title must be at most 200 characters` |
| 422 | `invalid_request` | free text describing the problem |
| 404 | `todo_not_found` | `This todo no longer exists` |
| 503 | `unavailable` | `Todos are unavailable, please try again` (database unreachable) |

todo-web branches on `code` and status, never on `message`. todo-web treats any 5xx, a connection error, or no
response within 5 seconds as "unavailable".

### Probes

- `GET /health` -> `200 {"status": "ok"}` whenever the process runs (no DB check).
- `GET /ready` -> `200 {"status": "ready"}` when the database answers; `503` otherwise.

### Configuration

| Repo | Variable | Value in `dev` | Set by |
|---|---|---|---|
| todo-api | `DATABASE_URL` (+ `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) | from Secret `todo-postgres-app` | postgres addon, `uses: [postgres]` |
| todo-web | `TODO_API_URL` | `http://todo-api` | `services.yaml` `env` |

No events: the only interaction is synchronous HTTP from todo-web to todo-api.

### Notes for this repo

Connection comes only from DATABASE_URL (CloudNativePG `uri`, scheme `postgresql://`), injected by the postgres
addon; PG* variables are also present. Add a Postgres driver (psycopg 3) through the repo's devbox/uv workflow;
if an ORM needs a dialect scheme (`postgresql+psycopg://`), rewrite it in code, never in gitops.
Create the `todos` table idempotently on startup (or with a migration run at startup); no manual DB steps.
`/ready` must return 503 while the database is unreachable; `/health` stays DB-independent.
Acceptance tests run against a real Postgres (testcontainers or a devbox-provided server), not SQLite.
Replace FastAPI's default 422 body with the error format of the contract. Document DATABASE_URL in docs/env-vars.md.

## Stories

- As todo-web, I want to list, create, mark done / not done and delete todos over HTTP, so that the todo list page can show and change the one shared list.
- As todo-web, I want every rejected request to come back with a stable error `code`, so that the page can show the right message ("Title is required", "Title must be at most 200 characters", "This todo no longer exists", "Todos are unavailable, please try again") without parsing free text.
- As a user of the todo list page, I want my todos to survive a restart or redeploy of todo-api, so that what I wrote down is still there.
- As the operator of the `dev` environment, I want todo-api to report not ready while its database is unreachable, so that no traffic is routed to a pod that cannot serve todos.

## Acceptance criteria

All error bodies below have the contract's shape `{"error": {"code": "<code>", "message": "<message>"}}` with `Content-Type: application/json`; "nothing is created / changed" means a following `GET /todos` returns the same list as before the request.

- **AC-001.1** Given no todos exist, when a caller sends `GET /todos`, then the response is `200` with the body `[]`. (product AC-001.3)
- **AC-001.2** Given three todos created one after another, when a caller sends `GET /todos`, then the response is `200` with a JSON array of the three todos, each with exactly the fields `id`, `title`, `done` and `created_at`, ordered by `created_at` ascending (oldest first) and, for equal `created_at`, by `id` ascending. (product AC-001.3)
- **AC-001.3** Given any state, when a caller sends `POST /todos` with `{"title": "Buy milk"}`, then the response is `201` with a todo whose `id` is a UUID v4 not used by any other todo, `title` is `"Buy milk"`, `done` is `false` and `created_at` is an RFC 3339 UTC timestamp (e.g. `2026-10-08T12:34:56.789Z`); the todo appears last in a following `GET /todos`. (product AC-001.3)
- **AC-001.4** Given a title with leading and trailing whitespace such as `"  Buy milk\t\n"`, when a caller sends `POST /todos` with it, then the response is `201` with `title` `"Buy milk"`, and `GET /todos` also returns `"Buy milk"`; inner spaces (`"Buy  milk"`) are kept as sent. (product AC-001.7)
- **AC-001.5** Given a `POST /todos` body whose `title` is missing, `null`, `""` or whitespace only (e.g. `"   "`), when it is sent, then the response is `422` with code `title_required` and message `Title is required`, and nothing is created. (product AC-001.5)
- **AC-001.6** Given a `POST /todos` title that has more than 200 Unicode code points after trimming (e.g. 201 × `a`, or 201 × `é`), when it is sent, then the response is `422` with code `title_too_long` and message `Title must be at most 200 characters`, and nothing is created. (product AC-001.6)
- **AC-001.7** Given a `POST /todos` title of exactly 200 code points after trimming (200 × `a`; 200 × `é`; 200 × `a` surrounded by spaces), when it is sent, then the response is `201` and the stored `title` has exactly 200 code points. (product AC-001.6)
- **AC-001.8** Given a `POST /todos` body that is not valid JSON, is a JSON value other than an object (e.g. `[]`, `"x"`), or has a `title` that is not a string (e.g. `42`, `true`, `["x"]`), when it is sent, then the response is `422` with code `invalid_request` and a non-empty `message`, and nothing is created; fields other than `title` in an otherwise valid body are ignored and the todo is created. (product AC-001.5)
- **AC-001.9** Given a todo with `done` `false`, when a caller sends `PATCH /todos/{id}` with `{"done": true}`, then the response is `200` with the todo and `done` `true`, its `id`, `title` and `created_at` unchanged, and a following `GET /todos` shows it with `done` `true`; sending `{"done": true}` again also answers `200` with `done` `true`. (product AC-001.8)
- **AC-001.10** Given a todo with `done` `true`, when a caller sends `PATCH /todos/{id}` with `{"done": false}`, then the response is `200` with `done` `false` and a following `GET /todos` shows it with `done` `false`; sending `{"done": false}` again also answers `200`. (product AC-001.9)
- **AC-001.11** Given an existing todo, when a caller sends `PATCH /todos/{id}` with a body that is not a JSON object, has no `done`, or has a `done` that is not a boolean (e.g. `"true"`, `1`, `null`), then the response is `422` with code `invalid_request`, and the todo is unchanged. (product AC-001.8)
- **AC-001.12** Given an existing todo, when a caller sends `DELETE /todos/{id}`, then the response is `204` with an empty body, the todo no longer appears in `GET /todos`, and every other todo is unchanged. (product AC-001.10)
- **AC-001.13** Given an id that belongs to no todo (a random UUID, an id that was already deleted, or a string that is not a UUID such as `abc`), when a caller sends `PATCH /todos/{id}` with a valid body or `DELETE /todos/{id}`, then the response is `404` with code `todo_not_found` and message `This todo no longer exists`, and nothing is created or changed. (product AC-001.11)
- **AC-001.14** Given todos created by one caller, when a second caller with different or no headers (no credentials, no cookies) sends `GET /todos`, then it receives the same todos; no endpoint asks for authentication. (product AC-001.13)
- **AC-001.15** Given an empty database that has never been used by todo-api, when todo-api starts with `DATABASE_URL` pointing at it, then it becomes ready and `GET /todos` answers `200 []` without any manual database step; starting it again against the same database keeps the existing todos. (product AC-001.14)
- **AC-001.16** Given todos exist, some done and some not, when todo-api is stopped and started again (a new process) against the same database, then `GET /todos` returns the same todos with the same `id`, `title`, `done`, `created_at` and order as before the restart. (product AC-001.14)
- **AC-001.17** Given the database is unreachable, when a caller sends any request to `/todos` or `/todos/{id}`, then todo-api answers `503` with code `unavailable` and message `Todos are unavailable, please try again` within 3 seconds; `GET /ready` answers `503` and `GET /health` answers `200 {"status": "ok"}`. (product AC-001.14)
- **AC-001.18** Given the database was unreachable and becomes reachable again, when a caller sends `GET /ready` and `GET /todos`, then `/ready` answers `200 {"status": "ready"}` and `/todos` serves the stored todos again, without restarting todo-api. (product AC-001.14)

## Non-goals

- Authentication, users, or more than one list (one shared list, per the product spec).
- Editing a todo's title, reordering, due dates, or any field beyond `id`, `title`, `done`, `created_at`.
- A single-todo read endpoint (`GET /todos/{id}`), paging, filtering or search on `GET /todos`.
- Limits on the number of todos.
- Exposing todo-api outside the environment (todo-web calls it server-side; exposure is the `todo` repo's concern).
- Configuring the database itself (provisioning, backups, version): owned by the postgres addon in the `todo` repo.
- Promotion to `staging` or `prod`.

## Open questions

- Confirm: when the database is unreachable, todo-api answers `503 unavailable` within 3 seconds rather than waiting longer, so todo-web gets the 503 before its own 5-second timeout. (suggested: yes, 3 seconds; affects AC-001.17)

## Changelog

- 2026-10-08 created
