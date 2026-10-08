"""FastAPI entry point for todo-api."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from .db import Database
from .errors import install_error_handlers
from .logging_config import configure_logging
from .metrics import REQUEST_COUNT
from .todos.repository import SCHEMA_SQL
from .todos.router import router as todos_router
from .tracing import configure_tracing, tracing_enabled

configure_logging(level=os.environ.get("LOG_LEVEL", "INFO"))
if tracing_enabled():
    configure_tracing()


class HealthResponse(BaseModel):
    status: str


def _resolve_database_url(database_url: str | None) -> str:
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def create_app(database_url: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        db = Database(_resolve_database_url(database_url), schema_sql=SCHEMA_SQL)
        await db.open()
        app.state.db = db
        try:
            yield
        finally:
            await db.close()

    app = FastAPI(title="todo-api", version="0.1.0", lifespan=lifespan)
    install_error_handlers(app)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Liveness probe — returns 200 as long as the process is responding."""
        return HealthResponse(status="ok")

    @app.get("/ready", response_model=HealthResponse)
    async def ready() -> HealthResponse:
        """Readiness probe — returns 200 when the database answers."""
        await app.state.db.ping()
        return HealthResponse(status="ready")

    @app.get("/ping")
    def ping() -> dict[str, str]:
        """Simple ping endpoint."""
        REQUEST_COUNT.labels(method="GET", endpoint="/ping", status_code="200").inc()
        return {"pong": "todo-api"}

    @app.get("/metrics")
    def metrics() -> Response:
        """Prometheus scrape endpoint."""
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(todos_router)
    return app


app = create_app()
