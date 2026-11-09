"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    resp = client.get("/todos/count")
    assert resp.status_code == 200
    assert resp.headers["content-type"].split(";")[0] == "application/json"
    assert resp.json() == {"count": 3}


def test_count_empty(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200
    assert resp.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    expected = {"code": "todo_not_found", "message": "This todo no longer exists"}
    patch = client.patch("/todos/count", json={"done": True})
    assert patch.status_code == 404
    assert patch.json() == {"error": expected}
    delete = client.delete("/todos/count")
    assert delete.status_code == 404
    assert delete.json() == {"error": expected}
