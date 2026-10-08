# Design — 001 Todo REST API persisted in Postgres

## Decisions

- **psycopg 3 async + `psycopg_pool.AsyncConnectionPool`, plain SQL, no ORM.** One table and four queries do not justify SQLAlchemy + Alembic. psycopg accepts the CloudNativePG `postgresql://` URI as is, so no scheme rewrite is needed. Async because AC-001.17 needs a hard response deadline: an awaited task can be abandoned after 2.5 s even when the socket hangs (paused or partitioned database), which a blocking driver call in a thread cannot. Dependency: `psycopg[binary,pool]>=3.2` (the binary wheel bundles libpq, so the `python:3.12-slim` image needs no system packages). ADR: [docs/adr/001-postgres-persistence.md](../../adr/001-postgres-persistence.md).
- **Schema created idempotently at startup, and lazily until it succeeds** (AC-001.15, AC-001.18). `CREATE TABLE IF NOT EXISTS` runs inside a transaction holding `pg_advisory_xact_lock`, so concurrent replicas cannot race. If the database is down at startup the process still starts (`/health` 200, `/ready` 503) and the schema is ensured on the first successful database operation. It never crash-loops on an unreachable database.
- **Every database operation runs under one deadline of 2.5 s** (AC-001.17, below the 3 s of the criterion and todo-web's 5 s). Pool checkout timeout is 2 s and libpq `connect_timeout=2`. A timeout, `PoolTimeout`, `psycopg.OperationalError` or `psycopg.InterfaceError` becomes `DatabaseUnavailable` → `503 unavailable`. Other psycopg errors are bugs → `500 internal_error`.
- **The pool checks connections on checkout** (`check=AsyncConnectionPool.check_connection`), so the first request after the database comes back does not get a dead connection (AC-001.18). The pool is opened with `wait=False` so startup never blocks on the database.
- **Request bodies are parsed by hand, not by a Pydantic model.** The contract's error codes depend on *which* rule fails (a `null` title → `title_required`, `42` → `invalid_request`), which FastAPI's validation cannot express. FastAPI's `RequestValidationError` handler is still replaced, as a safety net.
- **`created_at` is set by the database, truncated to milliseconds** (`date_trunc('milliseconds', clock_timestamp())`). The stored value then equals the serialized value, so ordering by `(created_at, id)` in SQL is exactly the ordering a client sees (AC-001.2). One clock for all replicas.
- **`id` is generated in Python (`uuid.uuid4()`)**: guarantees v4 (AC-001.3) without depending on server extensions.
- **Configuration is read in the lifespan, not at import**: `create_app(database_url: str | None = None)`. `None` means `os.environ["DATABASE_URL"]`, and a missing variable fails startup with a clear error. The module-level `app = create_app()` stays the uvicorn entry point. Tests can then start several app instances (restart, unreachable database) in one process.

## Modules

| Module | Responsibility | New / changed |
|---|---|---|
| `src/todo_api/errors.py` | `ApiError(status, code, message)`, `DatabaseUnavailable`, `install_error_handlers(app)` (ApiError, DatabaseUnavailable, RequestValidationError, Starlette HTTPException, unhandled Exception) | new |
| `src/todo_api/todos/__init__.py` | package marker (docstring only) | new |
| `src/todo_api/todos/validation.py` | pure functions: `parse_create(raw: bytes) -> str`, `parse_patch(raw: bytes) -> bool`, `parse_id(value: str) -> UUID \| None`; raise `ApiError` | new |
| `src/todo_api/todos/repository.py` | `Todo` dataclass; SQL on an `AsyncConnection`: `list_todos`, `create_todo`, `set_done`, `delete_todo`; DDL constant `SCHEMA_SQL` | new |
| `src/todo_api/db.py` | `Database`: pool lifecycle (`open`, `close`), `ensure_schema`, `run(op)` with the deadline and error mapping, `ping()` | new |
| `src/todo_api/todos/router.py` | `APIRouter` for `/todos`, serialization of `Todo` to the contract JSON | new |
| `src/todo_api/main.py` | `create_app()`, lifespan (open pool, try schema, close pool), `/ready` checks the database, include router, install error handlers | changed |
| `pyproject.toml`, `uv.lock` | `psycopg[binary,pool]>=3.2`; dev: `testcontainers[postgres]>=4.8` | changed |
| `docs/env-vars.md`, `README.md` | `DATABASE_URL`, `TEST_DATABASE_URL`; local run and tests need Postgres / Docker | changed |

Key signatures (types only, no implementation):

```python
# errors.py
class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None: ...
class DatabaseUnavailable(Exception): ...
def install_error_handlers(app: FastAPI) -> None: ...

# db.py
OP_DEADLINE_S = 2.5
class Database:
    def __init__(self, url: str, schema_sql: str) -> None: ...
    async def open(self) -> None: ...            # pool.open(wait=False), then try ensure_schema (log, never raise)
    async def close(self) -> None: ...
    async def run(self, op: Callable[[AsyncConnection], Awaitable[T]]) -> T: ...
        # ensure_schema if not done; checkout; op; commit — in one task awaited at most OP_DEADLINE_S.
        # On timeout the task is left to finish in the background (kept in a set, its exception consumed and
        # logged) and DatabaseUnavailable is raised. Connection-class errors -> DatabaseUnavailable.
    async def ping(self) -> None: ...            # SELECT 1 through run(); raises DatabaseUnavailable

# todos/repository.py
SCHEMA_SQL: str
@dataclass(frozen=True)
class Todo:
    id: UUID; title: str; done: bool; created_at: datetime
async def list_todos(conn: AsyncConnection) -> list[Todo]: ...
async def create_todo(conn: AsyncConnection, title: str) -> Todo: ...
async def set_done(conn: AsyncConnection, todo_id: UUID, done: bool) -> Todo | None: ...   # None = not found
async def delete_todo(conn: AsyncConnection, todo_id: UUID) -> bool: ...                    # False = not found

# main.py
def create_app(database_url: str | None = None) -> FastAPI: ...
app: FastAPI  # = create_app()
```

The `Database` instance lives on `app.state.db`; the router reads it from `request.app.state.db`.

## Contract

The spec's contract (Product context → Contract) is binding and is not repeated in full. This section fixes the details it leaves open. Testers write against both.

### Common

- All JSON responses: `Content-Type: application/json`. `DELETE` 204 has no body.
- Error body, always: `{"error": {"code": "<code>", "message": "<message>"}}`, no other keys.
- The request body is read as bytes and parsed as JSON regardless of the request's `Content-Type`. An empty body counts as "not valid JSON".

### Todo object serialization

| Field | Exact form |
|---|---|
| `id` | lowercase canonical UUID with hyphens, e.g. `"3f2b8c1e-9a4d-4c7e-8b1a-2d5e6f708192"` |
| `title` | stored trimmed title |
| `done` | JSON boolean |
| `created_at` | UTC, always exactly 3 fractional digits and `Z`: `YYYY-MM-DDTHH:MM:SS.mmmZ` |

Exactly these four keys (AC-001.2).

### `POST /todos`: rule order (first failing rule wins, no database access before step 7)

1. Body is not valid JSON → `422 invalid_request` (AC-001.8)
2. Body is not a JSON object → `422 invalid_request` (AC-001.8)
3. `title` key missing or `null` → `422 title_required` (AC-001.5)
4. `title` is not a string → `422 invalid_request` (AC-001.8)
5. `title.strip()` (Python `str.strip()`, no argument) is `""` → `422 title_required` (AC-001.4, AC-001.5)
6. `len(stripped) > 200` (code points, no Unicode normalization) → `422 title_too_long`; exactly 200 is accepted (AC-001.6, AC-001.7)
7. Insert → `201` Todo; database failure → `503 unavailable` (AC-001.3, AC-001.17)

Keys other than `title` are ignored (including `done`, `id`, `created_at`).

### `PATCH /todos/{id}`: rule order

1. Body is not valid JSON, not an object, `done` missing, or `done` not a JSON boolean (`"true"`, `1`, `null` are rejected) → `422 invalid_request` (AC-001.11)
2. `{id}` does not parse as a UUID (`uuid.UUID(value)`) → `404 todo_not_found` (AC-001.13)
3. `UPDATE ... RETURNING` finds no row → `404 todo_not_found`; database failure → `503 unavailable`
4. `200` updated Todo; setting the current value again is a no-op that still returns `200` (AC-001.9, AC-001.10)

### `DELETE /todos/{id}`

1. `{id}` not a UUID → `404 todo_not_found`
2. `DELETE` affects no row → `404 todo_not_found`; database failure → `503 unavailable`
3. `204`, empty body (AC-001.12)

### `GET /todos`

`200` array, `ORDER BY created_at ASC, id ASC` (Postgres `uuid` ordering equals lowercase-hex string ordering); `[]` when empty; database failure → `503 unavailable` (AC-001.1, AC-001.2).

### Database unavailable (AC-001.17)

Requests that pass validation and need the database answer `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}` within 2.5 s plus request overhead, well under 3 s. Requests rejected by validation (422, and 404 for a non-UUID id) are answered without the database, also while it is down. The acceptance tests for AC-001.17 therefore use valid requests and UUID ids.

### Probes

- `GET /health` → `200 {"status": "ok"}`; never touches the database.
- `GET /ready` → `200 {"status": "ready"}` when `SELECT 1` succeeds and the schema exists; otherwise `503 {"error": {"code": "unavailable", "message": "Todos are unavailable, please try again"}}`, same deadline (AC-001.17, AC-001.18).
- `/ping` and `/metrics` are unchanged.

### Errors outside the spec's table (same body format)

| HTTP | `code` | `message` | When |
|---|---|---|---|
| 404 | `not_found` | `Not found` | unknown route |
| 405 | `method_not_allowed` | `Method not allowed` | e.g. `PUT /todos` |
| 500 | `internal_error` | `Internal server error` | unexpected exception (logged with stack, never the DSN) |

### Test harness (written by the testers with the acceptance tests, in `tests/conftest.py`)

The coders rely on these names. The existing `tests/test_health.py` keeps passing through the replaced `client` fixture.

- `postgres_url` (session): `TEST_DATABASE_URL` if set, else the URL of a `testcontainers.postgres.PostgresContainer("postgres:17-alpine", driver=None)` (`postgresql://...`, the addon's major version). Docker is available on GitHub's `ubuntu-latest` runners, so `ci.yml` needs no change.
- autouse, per test: `DROP TABLE IF EXISTS todos`, so the "never used" database of AC-001.15 is the default state.
- `client`: `with TestClient(create_app(database_url=postgres_url)) as c: yield c` (the `with` runs the lifespan).
- Restart (AC-001.15, AC-001.16): leave the first `with TestClient(...)` block and enter a new one with a fresh `create_app(...)` against the same URL.
- Unreachable (AC-001.17): `create_app(database_url="postgresql://todo:todo@127.0.0.1:1/todo")` (connection refused), and a paused container (`container.get_wrapped_container().pause()`) for the hanging case.
- Recovery (AC-001.18): a function-scoped container; `pause()` → assert 503 → `unpause()` → assert `/ready` 200 and `/todos` serves the stored todos, same app instance. Pausing keeps the mapped port; stopping does not.

## Data

Table `todos`, defined by `SCHEMA_SQL` in `repository.py` and executed by `Database.ensure_schema()`:

```sql
CREATE TABLE IF NOT EXISTS todos (
    id         uuid        PRIMARY KEY,
    title      text        NOT NULL CHECK (char_length(title) BETWEEN 1 AND 200),
    done       boolean     NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT date_trunc('milliseconds', clock_timestamp())
);
CREATE INDEX IF NOT EXISTS todos_created_at_id_idx ON todos (created_at, id);
```

It runs in one transaction after `SELECT pg_advisory_xact_lock(<fixed bigint>)`. The CHECK mirrors the API rule as a last guard (the database is UTF-8, so `char_length` counts code points).

## Risks

- **Abandoned operations after a 503.** A write whose deadline expired may still commit when a paused database resumes. The client was told "unavailable" and sees the todo on the next reload. Accepted: todo-web never shows such a change as saved, and a reload shows the true state.
- **Same-millisecond creates.** Two todos created in the same millisecond are ordered by `id`, so "the new todo is last" (AC-001.3) holds only for creates at least 1 ms apart, which sequential HTTP calls always are.
- **Readiness probe timeout.** Kubernetes' default probe timeout (1 s) is shorter than the 2.5 s deadline. While the database hangs the probe times out instead of receiving the 503, which Kubernetes also treats as not ready. No gitops change needed.
- **Logging the DSN.** `DATABASE_URL` contains the password. It is never logged; connection errors are logged by class name.
- **Docker for local tests.** `devbox run test` now needs a Docker daemon (or `TEST_DATABASE_URL`); documented in the README.
