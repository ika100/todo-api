"""Acceptance tests for spec 900: count todos through GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str) -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_of_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        create(client, title)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 3}
    assert isinstance(body["count"], int)
    assert not isinstance(body["count"], bool)


def test_count_of_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 0}
    assert isinstance(body["count"], int)


def test_patch_count_is_unknown_id(client: TestClient):  # AC-900.2
    todo = create(client, "keep")
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == NOT_FOUND
    assert client.get("/todos").json() == [todo]


def test_delete_count_is_unknown_id(client: TestClient):  # AC-900.2
    todo = create(client, "keep")
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == NOT_FOUND
    assert client.get("/todos").json() == [todo]
