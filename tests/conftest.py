"""Shared pytest fixtures.

Database-backed fixtures follow docs/specs/001-*/design.md ("Test harness"). Heavy imports
(psycopg, testcontainers) are lazy so collection never fails for a missing dependency.
Until ``create_app(database_url=...)`` exists, ``client`` falls back to the module-level app so
the old smoke tests keep passing and the acceptance tests fail on missing behaviour.
"""

from __future__ import annotations

import inspect
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from fastapi.testclient import TestClient

UNREACHABLE_URL = "postgresql://todo:todo@127.0.0.1:1/todo"


def _factory() -> Callable[..., Any] | None:
    from todo_api import main

    create_app = getattr(main, "create_app", None)
    if create_app is None:
        return None
    if "database_url" not in inspect.signature(create_app).parameters:
        return None
    return create_app


def make_app(url: str) -> Any:
    """Build an app instance against ``url`` (fails while create_app is missing)."""
    from todo_api.main import create_app

    return create_app(database_url=url)


def new_container() -> Any:
    require_impl()
    from testcontainers.postgres import PostgresContainer

    return PostgresContainer("postgres:17-alpine", driver=None)


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """Real Postgres: TEST_DATABASE_URL, else a postgres:17-alpine testcontainer."""
    if _factory() is None:  # behaviour missing: tests fail in their body, not here
        yield ""
        return
    env = os.environ.get("TEST_DATABASE_URL")
    if env:
        yield env
        return
    with new_container() as container:
        yield container.get_connection_url()


def require_impl() -> None:
    assert _factory() is not None, "todo_api.main.create_app(database_url=...) is missing"


def drop_todos(url: str) -> None:
    require_impl()
    import psycopg

    with psycopg.connect(url, autocommit=True, connect_timeout=5) as conn:
        conn.execute("DROP TABLE IF EXISTS todos")


@pytest.fixture(autouse=True)
def _fresh_database(request: pytest.FixtureRequest) -> None:
    """Per test: drop the todos table so the database is "never used" by default."""
    if _factory() is None:
        return
    if "container_url" in request.fixturenames or "no_db" in request.fixturenames:
        return
    drop_todos(request.getfixturevalue("postgres_url"))


@pytest.fixture()
def no_db() -> None:
    """Marker fixture: the test manages its own database (skips the per-test drop)."""


@pytest.fixture()
def client(request: pytest.FixtureRequest) -> Iterator[TestClient]:
    """TestClient with the lifespan running, backed by the real Postgres."""
    create_app = _factory()
    if create_app is None:
        from todo_api.main import app

        yield TestClient(app)
        return
    url = request.getfixturevalue("postgres_url")
    with TestClient(create_app(database_url=url)) as c:
        yield c


@pytest.fixture()
def second_client(postgres_url: str) -> Iterator[Callable[[], TestClient]]:
    yield lambda: TestClient(make_app(postgres_url))


@contextmanager
def running(url: str) -> Iterator[TestClient]:
    """Start a fresh app instance (new 'process') against ``url``."""
    with TestClient(make_app(url)) as c:
        yield c


@pytest.fixture()
def container_url() -> Iterator[Any]:
    """Function-scoped Postgres container (for pause/unpause). Yields a starter callable."""
    started: list[Any] = []

    def start() -> Any:
        c = new_container()
        c.start()
        started.append(c)
        return c

    yield start
    for c in started:
        try:
            c.get_wrapped_container().unpause()
        except Exception:  # noqa: BLE001 - already running
            pass
        c.stop()
