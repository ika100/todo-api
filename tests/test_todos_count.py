"""Acceptance tests for spec 900: count todos through GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str) -> None:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text


def test_count_of_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        create(client, title)
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 3}


def test_count_of_no_todos(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 0}


def test_patch_count_is_unknown_id(client: TestClient):  # AC-900.2
    got = client.get("/todos/count")
    assert got.status_code == 200, got.text
    assert got.json() == {"count": 0}
    resp = client.patch("/todos/count", json={"done": True})
    assert resp.status_code == 404, resp.text
    assert resp.json() == NOT_FOUND


def test_delete_count_is_unknown_id(client: TestClient):  # AC-900.2
    got = client.get("/todos/count")
    assert got.status_code == 200, got.text
    assert got.json() == {"count": 0}
    resp = client.delete("/todos/count")
    assert resp.status_code == 404, resp.text
    assert resp.json() == NOT_FOUND
