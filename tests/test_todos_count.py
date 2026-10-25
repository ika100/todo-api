"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def _create(client: TestClient, title: str) -> None:
    assert client.post("/todos", json={"title": title}).status_code == 201


def test_count_three_todos(client: TestClient):  # AC-900.1
    for t in ("one", "two", "three"):
        _create(client, t)
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    _create(client, "keep")
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    r = client.delete("/todos/count")
    assert r.status_code == 404
    assert r.json() == NOT_FOUND
    assert len(client.get("/todos").json()) == 1
