"""Acceptance tests for spec 900: count todos with GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 3}
    assert type(body["count"]) is int


def test_count_zero_and_id_routes_not_shadowed(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 0}
    assert type(r.json()["count"]) is int

    patched = client.patch("/todos/count", json={"done": True})
    assert patched.status_code == 404, patched.text
    assert patched.json() == NOT_FOUND

    deleted = client.delete("/todos/count")
    assert deleted.status_code == 404, deleted.text
    assert deleted.json() == NOT_FOUND
