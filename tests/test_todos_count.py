"""Acceptance tests for spec 900: count todos with GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str) -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        create(client, title)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 3}
    assert type(body["count"]) is int


def test_count_includes_done_todos(client: TestClient):  # AC-900.1
    a = create(client, "a")
    create(client, "b")
    assert client.patch(f"/todos/{a['id']}", json={"done": True}).status_code == 200
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": len(client.get("/todos").json())} == {"count": 2}


def test_count_empty(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 0}
    assert type(r.json()["count"]) is int


def test_count_ignores_query_parameters(client: TestClient):  # AC-900.2
    create(client, "a")
    r = client.get("/todos/count", params={"done": "true", "limit": "0"})
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 1}


def test_patch_count_is_unknown_id(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND


def test_delete_count_is_unknown_id(client: TestClient):  # AC-900.2
    create(client, "a")
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
    assert len(client.get("/todos").json()) == 1
