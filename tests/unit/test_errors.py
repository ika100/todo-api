import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from todo_api.errors import ApiError, DatabaseUnavailable, install_error_handlers


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/api")
    async def api() -> None:
        raise ApiError(422, "title_required", "Title is required")

    @app.get("/db")
    async def db() -> None:
        raise DatabaseUnavailable

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("postgresql://u:secret@h/d")

    @app.get("/int/{n}")
    async def integer(n: int) -> None:
        return None

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("path", "method", "status", "code", "message"),
    [
        ("/api", "get", 422, "title_required", "Title is required"),
        ("/db", "get", 503, "unavailable", "Todos are unavailable, please try again"),
        ("/int/x", "get", 422, "invalid_request", "Request body is invalid"),
        ("/nope", "get", 404, "not_found", "Not found"),
        ("/api", "put", 405, "method_not_allowed", "Method not allowed"),
        ("/boom", "get", 500, "internal_error", "Internal server error"),
    ],
)
def test_error_body(
    client: TestClient, path: str, method: str, status: int, code: str, message: str
) -> None:
    r = client.request(method, path)
    assert r.status_code == status
    assert r.json() == {"error": {"code": code, "message": message}}
    assert "secret" not in r.text
