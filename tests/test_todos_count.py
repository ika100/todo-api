"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    # Fails until the count route exists: the GET must succeed alongside the 404s.
    assert client.get("/todos/count").status_code == 200
    patch = client.patch("/todos/count", json={"done": True})
    assert patch.status_code == 404
    assert patch.json() == NOT_FOUND
    delete = client.delete("/todos/count")
    assert delete.status_code == 404
    assert delete.json() == NOT_FOUND
