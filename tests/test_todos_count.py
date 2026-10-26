"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].split(";")[0] == "application/json"
    assert r.json() == {"count": 3}


def test_count_includes_done_todos(client: TestClient):  # AC-900.1
    first = client.post("/todos", json={"title": "a"}).json()
    client.post("/todos", json={"title": "b"})
    client.post("/todos", json={"title": "c"})
    assert client.patch(f"/todos/{first['id']}", json={"done": True}).status_code == 200
    r = client.get("/todos/count", params={"done": "false"})
    assert r.status_code == 200
    assert r.json() == {"count": 3}
    assert r.json()["count"] == len(client.get("/todos").json())


def test_count_empty(client: TestClient):  # AC-900.2
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
