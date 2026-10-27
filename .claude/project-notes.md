# Project notes

- `todo-api` is the backend of the todo system (gitops repo `ika100/todo`): it provides the `todo-api-rest` API (OpenAPI) that `todo-web` consumes, and stores todos in the system's `postgres` resource (`DATABASE_URL`).
- Changing the API contract affects `todo-web` (`app/_lib/todo-api.ts`); such changes start as a system spec in `ika100/todo`.
