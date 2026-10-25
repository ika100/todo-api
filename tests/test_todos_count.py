"""Acceptance tests for spec 900 (GET /todos/count). Each test names its criterion AC-900.n."""

from __future__ import annotations

from fastapi.testclient import TestClient

NOT_FOUND = {"error": {"code": "todo_not_found", "message": "This todo no longer exists"}}


def create(client: TestClient, title: str) -> dict:
    r = client.post("/todos", json={"title": title})
    assert r.status_code == 201, r.text
    return r.json()


def test_count_three_todos(client: TestClient):  # AC-900.1
    for title in ("one", "two", "three"):
        create(client, title)
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    body = r.json()
    assert body == {"count": 3}
    assert type(body["count"]) is int


def test_count_follows_creates_and_deletes(client: TestClient):  # AC-900.1
    a = create(client, "a")
    create(client, "b")
    assert client.get("/todos/count").json() == {"count": 2}
    assert client.delete(f"/todos/{a['id']}").status_code == 204
    assert client.get("/todos/count").json() == {"count": 1}


def test_count_empty(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_route_does_not_clash_with_id_routes(client: TestClient):  # AC-900.2
    todo = create(client, "keep")
    assert client.get("/todos/count").json() == {"count": 1}
    for resp in (client.patch("/todos/count", json={"done": True}), client.delete("/todos/count")):
        assert resp.status_code == 404, resp.text
        assert resp.json() == NOT_FOUND
    assert client.get("/todos").json() == [todo]
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.patch(f"/todos/{todo['id']}", json={"done": True}).status_code == 200
    assert client.delete(f"/todos/{todo['id']}").status_code == 204
