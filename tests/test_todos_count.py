"""Acceptance tests for spec 900: GET /todos/count."""

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
    assert r.json() == {"count": 3}


def test_count_of_no_todos(client: TestClient):  # AC-900.2
    r = client.get("/todos/count")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("application/json")
    assert r.json() == {"count": 0}


def test_count_route_does_not_shadow_id_routes(client: TestClient):  # AC-900.2
    r = client.patch("/todos/count", json={"done": True})
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND
    r = client.delete("/todos/count")
    assert r.status_code == 404, r.text
    assert r.json() == NOT_FOUND


def test_count_does_not_change_other_endpoints(client: TestClient):  # AC-900.2
    todo = create(client, "keep")
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.get("/todos").json() == [todo]
    done = client.patch(f"/todos/{todo['id']}", json={"done": True})
    assert done.status_code == 200, done.text
    assert client.get("/todos/count").json() == {"count": 1}
    assert client.delete(f"/todos/{todo['id']}").status_code == 204
    assert client.get("/todos/count").json() == {"count": 0}
