"""Acceptance tests for spec 900 (GET /todos/count)."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 3}
    assert isinstance(body["count"], int) and not isinstance(body["count"], bool)


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.json() == {"count": 0}


def test_patch_count_is_not_found(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_delete_count_is_not_found(client: TestClient):  # AC-900.2
    r = client.delete("/todos/count")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
