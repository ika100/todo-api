---
spec_id: 001-todo-rest-api-list-create-mark-done-not
shape: service-python
spec_hash: aa586698c309
summary: Todo REST API (list, create, mark done/not done, delete) on psycopg 3 + Postgres, with the contract's error format
  and a DB-aware /ready
tasks:
- id: t1
  title: Add psycopg 3 (binary, pool) and testcontainers dependencies
  files: [pyproject.toml, uv.lock]
  covers: [AC-001.15, AC-001.16]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Add the error model and request validation
  files: [src/todo_api/errors.py, src/todo_api/todos/__init__.py, src/todo_api/todos/validation.py]
  covers: [AC-001.4, AC-001.5, AC-001.6, AC-001.7, AC-001.8, AC-001.11, AC-001.13, AC-001.17]
  parallel_safe: true
  depends_on: []
  done: true
- id: t3
  title: Document DATABASE_URL and the Postgres test setup
  files: [docs/env-vars.md, README.md]
  covers: [AC-001.15]
  parallel_safe: true
  depends_on: []
  done: true
- id: t4
  title: Add the Database pool with deadline, error mapping and schema-on-startup
  files: [src/todo_api/db.py]
  covers: [AC-001.15, AC-001.16, AC-001.17, AC-001.18]
  parallel_safe: true
  depends_on: [t1, t2]
  done: true
- id: t5
  title: Add the todos table DDL and repository queries
  files: [src/todo_api/todos/repository.py]
  covers: [AC-001.1, AC-001.2, AC-001.3, AC-001.7, AC-001.9, AC-001.10, AC-001.12, AC-001.13, AC-001.16]
  parallel_safe: true
  depends_on: [t1]
- id: t6
  title: Add the /todos router and wire create_app, lifespan and /ready
  files: [src/todo_api/todos/router.py, src/todo_api/main.py]
  covers: [AC-001.1, AC-001.2, AC-001.3, AC-001.4, AC-001.5, AC-001.6, AC-001.7, AC-001.8, AC-001.9, AC-001.10, AC-001.11,
    AC-001.12, AC-001.13, AC-001.14, AC-001.15, AC-001.16, AC-001.17, AC-001.18]
  parallel_safe: true
  depends_on: [t2, t4, t5]
---

# Plan — 001 Todo REST API persisted in Postgres

Design and binding contract details: [design.md](design.md). ADR: [docs/adr/001-postgres-persistence.md](../../adr/001-postgres-persistence.md).

Levels: t1, t2, t3 → t4, t5 → t6. The acceptance tests and their harness (`tests/conftest.py`: `postgres_url`, per-test table drop, DB-backed `client`; see design "Test harness") are written by the testers before coding and are not edited by any task. No change to `.github/workflows/ci.yml` or `Dockerfile` is needed: GitHub's `ubuntu-latest` runners provide Docker for testcontainers, and `psycopg[binary]` bundles libpq.

## t1 — Add psycopg 3 (binary, pool) and testcontainers dependencies

**Files:** pyproject.toml, uv.lock
**Covers:** AC-001.15, AC-001.16
**Goal:** make the Postgres driver and the test container library available through the repo's devbox/uv workflow.

**Implementation notes:**
- `[project] dependencies`: add `"psycopg[binary,pool]>=3.2"`.
- `[project.optional-dependencies] dev`: add `"testcontainers[postgres]>=4.8"`.
- Do not run `uv add`/`pip` directly: edit `pyproject.toml`, then any `devbox run` (its init hook runs `uv sync --all-extras`) re-locks; commit the updated `uv.lock`.
- `devbox run audit` must stay clean.

**Done when:** `uv.lock` contains `psycopg`, `psycopg-binary`, `psycopg-pool` and `testcontainers`; `devbox run quality` and `devbox run security` pass.

## t2 — Add the error model and request validation

**Files:** src/todo_api/errors.py, src/todo_api/todos/__init__.py, src/todo_api/todos/validation.py
**Covers:** AC-001.4, AC-001.5, AC-001.6, AC-001.7, AC-001.8, AC-001.11, AC-001.13, AC-001.17
**Goal:** one place that produces the contract's error body for every failure, and pure parsing functions that apply the contract's rule order without touching the database.

**Implementation notes:**
- `errors.py`: `ApiError(status, code, message)`, `DatabaseUnavailable`, constants for the five contract messages, `install_error_handlers(app)` registering handlers for `ApiError`, `DatabaseUnavailable` (→ 503 `unavailable`, increments `ERROR_COUNT{error_type="database_unavailable"}`), `RequestValidationError` (→ 422 `invalid_request`), Starlette `HTTPException` (404 `not_found`, 405 `method_not_allowed`, other statuses keep their status with a generic code) and `Exception` (→ 500 `internal_error`, logged via structlog with stack, never the DSN).
- Body is always `{"error": {"code", "message"}}` as `JSONResponse`.
- `todos/__init__.py`: package docstring only (no imports, so it never depends on later tasks).
- `validation.py`: `parse_create(raw: bytes) -> str` (rules 1–6 of the design's POST order, returns the stripped title), `parse_patch(raw: bytes) -> bool` (rule 1 of PATCH; `isinstance(v, bool)` only), `parse_id(value: str) -> UUID | None` (`None` for non-UUIDs).
- Length is `len(title.strip())` in code points; no Unicode normalization.
- Unit tests for the parsers may be added as new files under `tests/unit/` (not acceptance tests).

**Done when:** `devbox run quality` passes; the parsers return the codes of the design's rule tables (verified end to end by the HTTP acceptance tests after t6).

## t3 — Document DATABASE_URL and the Postgres test setup

**Files:** docs/env-vars.md, README.md
**Covers:** AC-001.15
**Goal:** operators and developers know what todo-api needs to run and to test.

**Implementation notes:**
- `docs/env-vars.md`: new "Database" section: `DATABASE_URL` (required, no default; `postgresql://user:password@host:5432/db`; injected in the cluster by the postgres addon through `uses: [postgres]` from Secret `todo-postgres-app`; startup fails if unset; the table is created automatically). Mention `PG*` are also injected but not read. Add `TEST_DATABASE_URL` (tests only: use this Postgres instead of starting a testcontainer).
- `README.md`: quick start runs against a local Postgres (`DATABASE_URL=... devbox run -- uv run uvicorn ...`); `devbox run test` needs a running Docker daemon or `TEST_DATABASE_URL`; list the `/todos` endpoints with a link to the spec and design.

**Done when:** both files describe `DATABASE_URL` and the test prerequisite; `devbox run secrets-scan` passes (no real credentials in examples).

## t4 — Add the Database pool with deadline, error mapping and schema-on-startup

**Files:** src/todo_api/db.py
**Covers:** AC-001.15, AC-001.16, AC-001.17, AC-001.18
**Goal:** a `Database` object that owns the connection pool, guarantees every operation answers within 2.5 s, maps connection failures to `DatabaseUnavailable`, and creates the schema at startup or as soon as the database is reachable.

**Implementation notes:**
- Constructor `Database(url: str, schema_sql: str)`: the DDL is passed in by `main.py`, so this module does not import t5's file.
- `AsyncConnectionPool(url, min_size=1, max_size=5, open=False, timeout=2.0, kwargs={"connect_timeout": 2}, check=AsyncConnectionPool.check_connection)`; `open()` calls `pool.open(wait=False)` then tries `ensure_schema()` and only logs on failure.
- `run(op)`: one `asyncio` task doing (ensure schema if not yet done) → `pool.connection()` → `op(conn)` → commit; awaited with `asyncio.wait(..., timeout=OP_DEADLINE_S)` (2.5). On timeout keep the task in a module-level set with a done-callback that consumes and logs its exception, and raise `DatabaseUnavailable`.
- Map `TimeoutError`, `psycopg_pool.PoolTimeout`, `psycopg.OperationalError`, `psycopg.InterfaceError` to `DatabaseUnavailable`; let other exceptions propagate (→ 500).
- `ensure_schema()`: guarded by an `asyncio.Lock` and a `_schema_ready` flag; executes `SELECT pg_advisory_xact_lock(<fixed bigint>)` then `schema_sql` in one transaction.
- `ping()`: runs `SELECT 1` through `run`.
- `close()`: `pool.close(timeout=5)`.
- Never log the URL; log connection failures as `event="database_unavailable", error=<class name>`.

**Done when:** `devbox run quality` passes; the AC-001.15, AC-001.17 and AC-001.18 acceptance tests pass after t6.

## t5 — Add the todos table DDL and repository queries

**Files:** src/todo_api/todos/repository.py
**Covers:** AC-001.1, AC-001.2, AC-001.3, AC-001.7, AC-001.9, AC-001.10, AC-001.12, AC-001.13, AC-001.16
**Goal:** the table definition and the four parameterized queries, independent of HTTP.

**Implementation notes:**
- `SCHEMA_SQL`: exactly the DDL in the design's "Data" section (table with CHECK and millisecond `created_at` default, index on `(created_at, id)`).
- `Todo` frozen dataclass (`id: UUID, title: str, done: bool, created_at: datetime`); use a psycopg row factory (`class_row(Todo)`).
- `list_todos`: `SELECT id, title, done, created_at FROM todos ORDER BY created_at, id`.
- `create_todo(conn, title)`: `INSERT ... (id, title) VALUES (%s, %s) RETURNING ...` with `uuid.uuid4()`.
- `set_done(conn, id, done)`: `UPDATE todos SET done = %s WHERE id = %s RETURNING ...` → `Todo | None`.
- `delete_todo(conn, id)`: `DELETE FROM todos WHERE id = %s` → `cursor.rowcount == 1`.
- Only bound parameters, no string formatting of values (bandit clean).

**Done when:** `devbox run quality` and `devbox run bandit` pass; the list/create/patch/delete acceptance tests pass after t6.

## t6 — Add the /todos router and wire create_app, lifespan and /ready

**Files:** src/todo_api/todos/router.py, src/todo_api/main.py
**Covers:** AC-001.1, AC-001.2, AC-001.3, AC-001.4, AC-001.5, AC-001.6, AC-001.7, AC-001.8, AC-001.9, AC-001.10, AC-001.11, AC-001.12, AC-001.13, AC-001.14, AC-001.15, AC-001.16, AC-001.17, AC-001.18
**Goal:** expose the contract over HTTP and make the app start against `DATABASE_URL`, report readiness from the database, and answer every error in the contract format.

**Implementation notes:**
- `router.py`: `APIRouter(prefix="/todos")` with async handlers `GET ""`, `POST ""` (201), `PATCH "/{todo_id}"`, `DELETE "/{todo_id}"` (204, empty `Response`). Path parameter typed `str` (never `UUID`, which would make FastAPI answer 422). Read the raw body with `await request.body()` and pass it to t2's parsers; follow the design's rule order (PATCH: body first, then id).
- Database access only through `request.app.state.db.run(...)` with t5's functions; `None`/`False` from the repository → `ApiError(404, "todo_not_found", ...)`.
- Serialization helper `to_json(todo) -> dict`: lowercase UUID string, `created_at` as `YYYY-MM-DDTHH:MM:SS.mmmZ` in UTC, exactly four keys.
- `main.py`: `create_app(database_url: str | None = None) -> FastAPI`; the lifespan resolves the URL (argument, else `os.environ["DATABASE_URL"]`, else raise `RuntimeError("DATABASE_URL is not set")`), builds `Database(url, schema_sql=SCHEMA_SQL)`, `await db.open()`, stores it on `app.state.db`, closes it on shutdown. Module-level `app = create_app()` stays the uvicorn entry point (no I/O at import).
- Keep logging/tracing setup, `/health` (no DB), `/ping`, `/metrics` unchanged; `/ready` becomes async, calls `db.ping()` and returns `{"status": "ready"}` (503 through the `DatabaseUnavailable` handler otherwise).
- Call `install_error_handlers(app)` and `app.include_router(router)` inside `create_app`.

**Done when:** every acceptance test for AC-001.1 to AC-001.18 and the existing `tests/test_health.py` / `tests/test_tracing.py` pass with `devbox run test`; `devbox run quality` and `devbox run security` pass.
