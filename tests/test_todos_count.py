"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    # The new route must exist (GET works) and PATCH/DELETE on the literal id stay 404.
    assert client.get("/todos/count").status_code == 200
    patch = client.patch("/todos/count", json={"done": True})
    assert patch.status_code == 404, patch.text
    assert patch.json() == NOT_FOUND
    delete = client.delete("/todos/count")
    assert delete.status_code == 404, delete.text
    assert delete.json() == NOT_FOUND
