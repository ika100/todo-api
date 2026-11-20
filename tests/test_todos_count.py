"""Acceptance tests for spec 900: count todos with GET /todos/count."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str = "Buy milk") -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_three_todos(client: TestClient):  # AC-900.1
    todos = [create(client, title) for title in ("a", "b", "c")]
    assert client.patch(f"/todos/{todos[1]['id']}", json={"done": True}).status_code == 200
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}
    assert type(r.json()["count"]) is int


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}
    assert type(r.json()["count"]) is int


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    create(client)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 1}
    assert type(r.json()["count"]) is int
    patched = client.patch("/todos/count", json={"done": True})
    assert patched.status_code == 404, patched.text
    assert patched.json() == NOT_FOUND
    deleted = client.delete("/todos/count")
    assert deleted.status_code == 404, deleted.text
    assert deleted.json() == NOT_FOUND
    for unknown in ("999999", str(uuid.uuid4())):
        p = client.patch(f"/todos/{unknown}", json={"done": True})
        assert (p.status_code, p.json()) == (patched.status_code, patched.json())
        d = client.delete(f"/todos/{unknown}")
        assert (d.status_code, d.json()) == (deleted.status_code, deleted.json())
