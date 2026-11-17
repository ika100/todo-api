"""Acceptance tests for spec 900: count todos with GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_of_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_of_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND


def test_count_route_registered_and_id_routes_kept(client: TestClient):  # AC-900.2
    created = client.post("/todos", json={"title": "keep"}).json()
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.patch(f"/todos/{created['id']}", json={"done": True}).status_code == 200
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.delete(f"/todos/{created['id']}").status_code == 204
    assert client.get("/todos/count").json() == {"count": 0}
