"""Acceptance tests for spec 900: count todos through GET /todos/count."""

from __future__ import annotations

from conftest import require_impl
from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str) -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_three_todos(client: TestClient):  # AC-900.1
    require_impl()
    for title in ("a", "b", "c"):
        create(client, title)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_zero_todos(client: TestClient):  # AC-900.2
    require_impl()
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    require_impl()
    todo = create(client, "keep")
    assert client.get("/todos/count").status_code == 200
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
    assert client.get("/todos").json() == [todo]
    assert client.get("/todos/count").json() == {"count": 1}
