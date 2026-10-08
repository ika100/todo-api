# todo-api

REST API for todo lists (create, list, complete, delete todos)

Owned by @ika100.

## Quick start

```bash
devbox shell                  # enter the dev environment
devbox run quality            # ruff + mypy
devbox run test               # pytest with coverage (needs Docker or TEST_DATABASE_URL)
DATABASE_URL=postgresql://user:password@localhost:5432/todos \
  devbox run -- uv run uvicorn todo_api.main:app --reload --port 8080
```

`DATABASE_URL` is required (see `docs/env-vars.md`); point it at a local Postgres. Then `curl http://localhost:8080/ping`.

## Testing

`devbox run test` starts a Postgres testcontainer, so a running Docker daemon is required. Without Docker, set `TEST_DATABASE_URL` to an existing Postgres instead.

## API

- `GET /todos` list todos
- `POST /todos` create a todo
- `PATCH /todos/{id}` mark a todo done
- `DELETE /todos/{id}` delete a todo

Details: [spec](docs/specs/001-todo-rest-api-list-create-mark-done-not/spec.md) and [design](docs/specs/001-todo-rest-api-list-create-mark-done-not/design.md).

## Conventions

- Config from environment variables only
- `/health` (liveness) and `/ready` (readiness) on every HTTP service
- Structured JSON logging
- `devbox run <script>` is the only sanctioned entry point for tooling

See `CLAUDE.md` for the full agent workflow and `devbox.json` for the canonical recipes.

## Deploy

| Target | Command |
|---|---|
| Staging / prod | Open a PR in the platform gitops repo or `/gitops:promote todo-api <from> <to>` |

Image: `ghcr.io/ika100/todo-api` — built and tagged automatically by CI.
