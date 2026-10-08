# ADR-001: Postgres persistence with psycopg 3 (async), plain SQL and schema-on-startup

## Status

Accepted (spec 001-todo-rest-api-list-create-mark-done-not).

## Context

todo-api must keep todos in the product's Postgres, provided by the gitops repo's postgres addon (CloudNativePG), which injects `DATABASE_URL` (`postgresql://...`) and `PG*`. No manual database steps are allowed, the service must report not ready (and answer `503` within 3 s) while the database is unreachable, and recover without a restart. The data model is one table with four queries. Acceptance tests must run against a real Postgres, locally and in GitHub Actions.

## Decision

- Driver: `psycopg[binary,pool]` 3, async, with `psycopg_pool.AsyncConnectionPool` (opened without waiting, connections checked on checkout). No ORM: SQL lives in a small repository module.
- Every database operation runs under one deadline (2.5 s); connection-class failures and timeouts map to one `DatabaseUnavailable` error, answered as `503 unavailable`.
- Schema: idempotent DDL (`CREATE ... IF NOT EXISTS`) under a Postgres advisory lock, run at startup and retried lazily until it succeeds. The first change to an existing table introduces a numbered migration runner (still executed at startup) in its own ADR.
- `/health` never touches the database; `/ready` reflects database connectivity.
- Tests: testcontainers (`postgres:17-alpine`, matching the addon) with a `TEST_DATABASE_URL` override; GitHub's runners provide Docker, so CI needs no extra service.

## Consequences

**Positive:** no dialect-scheme rewriting, no migration tool to operate, a guaranteed response deadline even when the database hangs, and tests that exercise the real database.

**Negative:** schema evolution beyond additive DDL needs the migration runner mentioned above; SQL is hand-written; running the test suite needs a Docker daemon (or an external Postgres via `TEST_DATABASE_URL`).
