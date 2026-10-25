"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 0}


def test_count_does_not_shadow_patch(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_count_does_not_shadow_delete(client: TestClient):  # AC-900.2
    r = client.delete("/todos/count")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND


def test_count_route_exists_alongside_unchanged_list(client: TestClient):  # AC-900.2
    client.post("/todos", json={"title": "one"})
    assert len(client.get("/todos").json()) == 1
    assert client.get("/todos/count").json() == {"count": 1}
