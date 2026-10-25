"""Acceptance tests for spec 900: count the todos with GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = ("todo_not_found", "This todo no longer exists")


def create(client: TestClient, title: str) -> None:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text


def assert_not_found(resp) -> None:
    assert resp.status_code == 404, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == NOT_FOUND[0]
    assert body["error"]["message"] == NOT_FOUND[1]


def test_count_three_todos(client: TestClient) -> None:  # AC-900.1
    for title in ("one", "two", "three"):
        create(client, title)
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 3}


def test_count_no_todos(client: TestClient) -> None:  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 0}


def test_patch_count_is_todo_not_found(client: TestClient) -> None:  # AC-900.2
    assert_not_found(client.patch("/todos/count", json={"done": True}))


def test_delete_count_is_todo_not_found(client: TestClient) -> None:  # AC-900.2
    assert_not_found(client.delete("/todos/count"))
