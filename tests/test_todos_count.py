"""Acceptance tests for spec 900: GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND_MSG = "This todo no longer exists"


def assert_not_found(resp) -> None:
    assert resp.status_code == 404, resp.text
    body = resp.json()
    assert body["error"]["code"] == "todo_not_found"
    assert body["error"]["message"] == NOT_FOUND_MSG


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        assert client.post("/todos", json={"title": title}).status_code == 201
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"count": 3}


def test_count_no_todos(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert body == {"count": 0}
    assert type(body["count"]) is int


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    assert_not_found(client.patch("/todos/count", json={"done": True}))
    assert_not_found(client.delete("/todos/count"))
