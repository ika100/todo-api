"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str) -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_three_todos(client: TestClient):  # AC-900.1
    for t in ("one", "two", "three"):
        create(client, t)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_includes_done_todos(client: TestClient):  # AC-900.1
    first = create(client, "one")
    create(client, "two")
    assert client.patch(f"/todos/{first['id']}", json={"done": True}).status_code == 200
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 2}


def test_count_empty(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 0}


def test_patch_count_is_not_found(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND


def test_delete_count_is_not_found(client: TestClient):  # AC-900.2
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
