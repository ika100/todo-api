"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from conftest import UNREACHABLE_URL  # noqa: F401
from fastapi.testclient import TestClient
from test_todos_api import NOT_FOUND, create


def test_count_three_todos(client: TestClient):  # AC-900.1
    for t in ("a", "b", "c"):
        create(client, t)
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.json() == {"count": 0}


def test_count_route_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    keep = create(client)
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    r = client.delete("/todos/count")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    assert client.get("/todos").json() == [keep]
    assert client.get("/todos/count").json() == {"count": 1}
