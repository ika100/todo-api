"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient) -> None:  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 3}


def test_count_zero_todos(client: TestClient) -> None:  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient) -> None:  # AC-900.2
    # Require the new route to exist so this fails now, not by accident.
    assert client.get("/todos/count").status_code == 200
    patched = client.patch("/todos/count", json={"done": True})
    assert patched.status_code == 404, patched.text
    assert patched.json() == NOT_FOUND
    deleted = client.delete("/todos/count")
    assert deleted.status_code == 404, deleted.text
    assert deleted.json() == NOT_FOUND
