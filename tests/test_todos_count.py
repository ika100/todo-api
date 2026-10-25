"""Acceptance tests for spec 900: count the todos with GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND_BODY = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def _create(client: TestClient, title: str) -> None:
    resp = client.post("/todos", json={"title": title})
    assert resp.status_code == 201, resp.text


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        _create(client, title)
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 0}


def test_patch_count_is_todo_not_found(client: TestClient):  # AC-900.2
    resp = client.patch("/todos/count", json={"done": True})
    assert resp.status_code == 404, resp.text
    assert resp.json() == NOT_FOUND_BODY


def test_delete_count_is_todo_not_found(client: TestClient):  # AC-900.2
    resp = client.delete("/todos/count")
    assert resp.status_code == 404, resp.text
    assert resp.json() == NOT_FOUND_BODY


def test_existing_endpoints_unchanged(client: TestClient):  # AC-900.2
    _create(client, "keep me")
    resp = client.get("/todos")
    assert resp.status_code == 200
    items = resp.json()
    assert [t["title"] for t in items] == ["keep me"]
    assert client.get("/todos/count").json() == {"count": 1}
