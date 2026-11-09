"""Acceptance tests for spec 900: count todos with GET /todos/count."""

from __future__ import annotations

from fastapi.testclient import TestClient


def create(client: TestClient, title: str) -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def assert_not_found(resp) -> None:
    assert resp.status_code == 404, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {
        "error": {"code": "todo_not_found", "message": "This todo no longer exists"}
    }


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("a", "b", "c"):
        create(client, title)
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert body == {"count": 3}
    assert type(body["count"]) is int


def test_count_follows_deletes(client: TestClient):  # AC-900.1
    first = create(client, "a")
    create(client, "b")
    assert client.get("/todos/count").json() == {"count": 2}
    assert client.delete(f"/todos/{first['id']}").status_code == 204
    assert client.get("/todos/count").json() == {"count": 1}


def test_count_empty(client: TestClient):  # AC-900.2
    resp = client.get("/todos/count")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert body == {"count": 0}
    assert type(body["count"]) is int


def test_count_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    # The GET must work (route exists) while PATCH/DELETE keep the unknown-id answer.
    assert client.get("/todos/count").status_code == 200
    assert_not_found(client.patch("/todos/count", json={"done": True}))
    assert_not_found(client.delete("/todos/count"))
    assert client.get("/todos/count").json() == {"count": 0}


def test_count_route_leaves_existing_endpoints_unchanged(client: TestClient):  # AC-900.2
    created = create(client, "keep me")
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.get("/todos").json() == [created]
