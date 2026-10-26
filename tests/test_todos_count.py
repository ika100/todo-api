"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def _create(client: TestClient, title: str) -> None:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text


def test_count_three_todos_returns_count(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        _create(client, title)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 3}


def test_count_counts_done_and_open_todos(client: TestClient):  # AC-900.1
    _create(client, "a")
    _create(client, "b")
    todo_id = client.get("/todos").json()[0]["id"]
    assert client.patch(f"/todos/{todo_id}", json={"done": True}).status_code == 200
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.json() == {"count": 2}


def test_count_empty_is_zero(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_patch_count_is_todo_not_found(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND


def test_delete_count_is_todo_not_found(client: TestClient):  # AC-900.2
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
